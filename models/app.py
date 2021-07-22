# this is a script to launch the app

import os
import fasttext
import json
from flask import Flask, jsonify, request
from dotenv import load_dotenv, find_dotenv

# load environment variables
load_dotenv(find_dotenv())

use_ceph = True
threshold = 0.6

application = Flask(__name__)

# read in bots
with open('botlist.txt', 'r') as f:
    bots = [bot.replace('\n', '') for bot in f.readlines()]

# read in label names
with open('labellist.txt', 'r') as f:
    labels = [lbl.replace('\n', '') for lbl in f.readlines()]

@application.route('/predict', methods=['POST'])
def predict():
    data = request.get_json() or '{}'
    data = json.loads(data)
    title, body, creator = data['title'], data['body'], data['created_by']
    if creator in bots:
        return ''
    ret = []
    body = body.replace('\r', '<R>').replace('\n', '<N>')
    input_ = title + '<SEP>' + body
 
    if use_ceph:
        s3_endpoint_url = os.environ["OBJECT_STORAGE_ENDPOINT_URL"]
        s3_access_key = os.environ["AWS_ACCESS_KEY_ID"]
        s3_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
        s3_bucket = os.environ["OBJECT_STORAGE_BUCKET_NAME"]
        s3 = boto3.client(
        service_name="s3",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        endpoint_url=s3_endpoint)
        for lbl in labels:
            path = os.path.join('saved_models', lbl.replace('/', '_') + '.bin')
            model = s3.get_object(Bucket=s3_bucket, Key=path)
            with open(path, 'wb') as f:
                for i in model['Body']:
                    f.write(i)
            model = fasttext.load_model(path)
            pred, prob = model.predict(input_)
            if pred[0] == '__label__0' and prob > threshold:
                print(prob)
                ret.append(lbl)
            os.remove(path)

    else:        
        for lbl in labels:
            path = os.path.join('saved_models', lbl.replace('/', '_') + '.bin')
            model = fasttext.load_model(path)
            pred, prob = model.predict(input_)
            if pred[0] == '__label__0' and prob > threshold:
                print(prob)
                ret.append(lbl)
    return '\t'.join(ret)


@application.route('/')
@application.route('/status')
def status():
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    application.run(debug=True)
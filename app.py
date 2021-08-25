"""This is a simple script with a predict function to launch the app."""

import os
import fasttext
import json
import logging
from flask import Flask, request, redirect
from dotenv import load_dotenv, find_dotenv
import boto3

_LOGGER = logging.getLogger('github-labeler')

# load environment variables
load_dotenv(find_dotenv())

use_ceph = True
threshold = 0.6

if use_ceph:
    s3_endpoint_url = os.environ["OBJECT_STORAGE_ENDPOINT_URL"]
    s3_access_key = os.environ["AWS_ACCESS_KEY_ID"]
    s3_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    s3_bucket = os.environ["OBJECT_STORAGE_BUCKET_NAME"]
    s3 = boto3.client(
        service_name="s3",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        endpoint_url=s3_endpoint_url,
    )

application = Flask('github-labeler')

@application.before_first_request
def before_first_request_callback():
    """Register callback, runs before first request to this service."""
    model_version_metric.set(1)
    _LOGGER.info("Running once before first request to expose metric.")


@application.after_request
def extend_response_headers(response):
    """Just add my signature."""
    response.headers["GITHUB-LABELER-VERSION"] = f"v{__version__}"
    return response

# read in bots

if use_ceph:
    lbllist = s3.get_object(Bucket=s3_bucket, Key="github_labeler/labellist.txt")
    with open("labellist.txt", "wb") as f:
        for i in lbllist["Body"]:
            f.write(i)
    botlist = s3.get_object(Bucket=s3_bucket, Key="github_labeler/botlist.txt")
    with open("botlist.txt", "wb") as f:
        for i in botlist["Body"]:
            f.write(i)


with open("botlist.txt", "r") as h:
    bots = [bot.replace("\n", "") for bot in h.readlines()]

# read in label names
with open("labellist.txt", "r") as h:
    labels = [lbl.replace("\n", "") for lbl in h.readlines()]


@application.route("/predict", methods=["POST", "GET"])
def predict():
    """Take json data of title, body, created_by and returns a tab separated list of strings."""
    if request.method == 'POST':
        data = request.get_json() or "{}"
        data = json.loads(data)
        title, body, creator = data["title"], data["body"], data["created_by"]
        if creator in bots:
            return ""
        ret = []
        body = body.replace("\r", "<R>").replace("\n", "<N>")
        input_ = title + "<SEP>" + body

        if use_ceph:
            for lbl in labels:
                path = os.path.join("saved_models", lbl.replace("/", "_") + ".bin")
                model = s3.get_object(Bucket=s3_bucket, Key=path)
                with open(path, "wb") as f:
                    for i in model["Body"]:
                        f.write(i)
                model = fasttext.load_model(path)
                pred, prob = model.predict(input_)
                if pred[0] == "__label__0" and prob > threshold:
                    print(prob)
                    ret.append(lbl)
                os.remove(path)

        else:
            for lbl in labels:
                path = os.path.join("saved_models", lbl.replace("/", "_") + ".bin")
                model = fasttext.load_model(path)
                pred, prob = model.predict(input_)
                if pred[0] == "__label__0" and prob > threshold:
                    print(prob)
                    ret.append(lbl)
        return "\t".join(ret)
    else:
        return 'ALL GOOD'


if __name__ == "__main__":
    _LOGGER.debug("Debug mode is on")
    application.run(host="0.0.0.0", port=8080)

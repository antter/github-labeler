"""This is a simple script with a predict function to launch the app."""

import os
import fasttext
import json
from flask import Flask, request
from dotenv import load_dotenv, find_dotenv
import boto3
import joblib

# load environment variables
load_dotenv(find_dotenv())

use_ceph = True
threshold = 0.6

name = os.getenv("REPO_NAME")

if "/" in name:
    REPO = name
    USER = ""
else:
    USER = name
    REPO = ""
savename = USER if USER else REPO.replace("/", "-_-")

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

application = Flask(__name__)

# read in bots & labels

if use_ceph:
    lbllist = s3.get_object(
        Bucket=s3_bucket, Key=f"github_labeler/{savename}/labellist.txt"
    )
    with open("labellist.txt", "wb") as f:
        for i in lbllist["Body"]:
            f.write(i)
    botlist = s3.get_object(
        Bucket=s3_bucket, Key=f"github_labeler/{savename}/botlist.txt"
    )
    with open("botlist.txt", "wb") as f:
        for i in botlist["Body"]:
            f.write(i)


with open("botlist.txt", "r") as h:
    bots = [bot.replace("\n", "") for bot in h.readlines()]

# read in label names
with open("labellist.txt", "r") as h:
    labels = [lbl.replace("\n", "") for lbl in h.readlines()]


@application.route("/predict", methods=["POST"])
def predict():
    """Take json data of title, body, created_by and returns a tab separated list of strings."""
    data = request.get_json() or "{}"
    data = json.loads(data)
    title, body, creator = data["title"], data["body"], data["created_by"]
    if creator in bots:
        return ""
    ret = []
    body = body.replace("\r", "<R>").replace("\n", "<N>")
    input_ = title + "<SEP>" + body

    filename = {"ft": ".bin", "svm": ".joblib"}
    if use_ceph:
        for lbl_type in labels:
            lbl, mod = lbl_type.split("\t")
            path = os.path.join("saved_models", lbl.replace("/", "_") + filename[mod])
            model = s3.get_object(
                Bucket=s3_bucket, Key=f"github-labeler/{savename}/{path}"
            )
            with open(path, "wb") as f:
                for i in model["Body"]:
                    f.write(i)
            if mod == "ft":
                model = fasttext.load_model(path)
                pred, prob = model.predict(input_)
                if pred[0] == "__label__0" and prob > threshold:
                    ret.append(lbl)
            else:
                model = joblib.load(path)
                pred = model.predict(input_)
                if pred[0] == 0:
                    ret.append(lbl)
            os.remove(path)

    else:
        for lbl_type in labels:
            lbl, mod = lbl_type.split("\t")
            path = os.path.join("saved_models", lbl.replace("/", "_") + filename[mod])
            with open(path, "wb") as f:
                for i in model["Body"]:
                    f.write(i)
            if mod == "ft":
                model = fasttext.load_model(path)
                if pred[0] == "__label__0" and prob > threshold:
                    ret.append(lbl)
            else:
                model = joblib.load(path)
                pred = model.predict(input_)
                if pred[0] == 0:
                    ret.append(lbl)
            os.remove(path)
    return "\t".join(ret)


if __name__ == "__main__":
    application.run(debug=True)

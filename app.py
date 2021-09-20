"""This is a simple script with a predict function to launch the app."""

import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv
import boto3
import joblib
from models.model_classes import FtModel
import sys

sys.path.append("./models")

# load environment variables
load_dotenv(find_dotenv())


# for unpickling tfidf object
def dummy_fun(x):
    """Return the input as a hacky fix to pickling a tf-idf object that uses tokenized text."""
    return x


use_ceph = True
threshold = 0.6

name = os.getenv("REPO_NAME")

if not os.path.isdir("models/saved_models"):
    os.path.mkdir("models/saved_models")

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
        Bucket=s3_bucket, Key=f"github-labeler/{savename}/labellist.txt"
    )
    with open("labellist.txt", "wb") as f:
        for i in lbllist["Body"]:
            f.write(i)
    botlist = s3.get_object(
        Bucket=s3_bucket, Key=f"github-labeler/{savename}/botlist.txt"
    )
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
    data = request.get_json() or "{}"
    data = json.loads(data)
    title, body, creator = data["title"], data["body"], data["created_by"]
    if creator in bots:
        return ""
    ret = []
    filename = {"ft": ".bin", "svm": ".joblib"}
    if request.method == "POST":
        if use_ceph:
            for lbl_type in labels:
                lbl, mod = lbl_type.split("\t")
                path = os.path.join(
                    "saved_models", lbl.replace("/", "_") + filename[mod]
                )
                model = s3.get_object(
                    Bucket=s3_bucket, Key=f"github-labeler/{savename}/{path}"
                )
                with open(os.path.join("models", path), "wb") as f:
                    for i in model["Body"]:
                        f.write(i)
                if mod == "ft":
                    model = FtModel(os.path.join("models", path))
                    pred = model.inference(title, body)
                    if pred == 1:
                        ret.append(lbl)
                else:
                    model = joblib.load(os.path.join("models", path))
                    pred = model.inference(title, body)
                    if pred == 1:
                        ret.append(lbl)
                os.remove(os.path.join("models", path))

        else:
            for lbl_type in labels:
                lbl, mod = lbl_type.split("\t")
                path = os.path.join(
                    "saved_models", lbl.replace("/", "_") + filename[mod]
                )
                with open(os.path.join("models", path), "wb") as f:
                    for i in model["Body"]:
                        f.write(i)
                if mod == "ft":
                    model = FtModel(os.path.join("models", path))
                    model.inference(title, body)
                    if pred == 1:
                        ret.append(lbl)
                else:
                    model = joblib.load(os.path.join("models", path))
                    model.inference(title, body)
                    if pred == 1:
                        ret.append(lbl)
    else:
        return (
            jsonify({"status": "ready"}),
            200,
            {"ContentType": "application/json"},
        )

    return "\t".join(ret)


if __name__ == "__main__":
    application.run(debug=True)

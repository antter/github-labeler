"""This file contains both the models that are used in github issue label predictions, fastText and an SVM."""

import fasttext
import numpy as np
from skift import FirstColFtClassifier
from sklearn.svm import SVC
import sys
import os
import boto3
from dotenv import load_dotenv, find_dotenv
import joblib


sys.path.append("../src/data")  # noqa
sys.path.append("./src/data")  # noqa
from preprocess import process  # noqa

load_dotenv(find_dotenv())

use_ceph = bool(int(os.getenv("USE_CEPH")))

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

name = os.getenv("REPO_NAME")

if "/" in name:
    REPO = name
    USER = ""
else:
    USER = name
    REPO = ""
savename = USER if USER else REPO.replace("/", "-_-")


class FtModel(FirstColFtClassifier):
    """This model is written over the skift column first classifier."""

    def __init__(self, path=""):
        """Initialize the model."""
        if not path:
            super().__init__()
        else:
            model = fasttext.load_model(path)
            setattr(self, "model", model)

    def preprocess(self, x):
        """Preprocess the text from a dataframe with processed column."""
        ret = np.array(x.processed.apply(lambda x: " ".join(x))).reshape(-1, 1)
        return ret

    def fit(self, x, y):
        """Fit the model."""
        input_ = self.preprocess(x)
        super().fit(input_, y)

    def predict(self, x):
        """Predict the output."""
        input_ = self.preprocess(x)
        return super().predict(input_)

    def save(self, path):
        """Save the model."""
        return self.model.save_model(path)

    def inference(self, title, body):
        """Inference for the app."""
        input_ = np.array(process(title, body)).reshape(1, -1)
        pred = super().predict(input_)
        return pred[0]


class SVM(SVC):
    """This model is built over the sklearn SVM classifier."""

    def __init__(self):
        """Initialize and load in the tfidf model."""
        super().__init__()
        if use_ceph:
            path = "tfidf.joblib"
            tfidf_file = s3.get_object(
                Bucket=s3_bucket, Key=f"github-labeler/{savename}/{path}"
            )
            with open(path, "wb") as f:
                for i in tfidf_file["Body"]:
                    f.write(i)
        self.tfidf = joblib.load("tfidf.joblib")

    def preprocess(self, x):
        """Tfidf transform the processed column of the dataframe inputted."""
        ret = self.tfidf.transform(x.processed)
        return ret

    def fit(self, x, y):
        """Fit the model."""
        input_ = self.preprocess(x)
        super().fit(input_, y)

    def predict(self, x):
        """Predict the output."""
        input_ = self.preprocess(x)
        return super().predict(input_)

    def save(self, path):
        """Save the model."""
        return joblib.dump(self, path)

    def inference(self, title, body):
        """Inference for the app."""
        input_ = np.array(process(title, body)).reshape(1, -1)
        input_ = self.tfidf.transform(input_)
        pred = super().predict(input_)
        return pred[0]

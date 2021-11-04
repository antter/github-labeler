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
from nltk.tokenize import word_tokenize

sys.path.append("../src/data")  # noqa
sys.path.append("./src/data")  # noqa
from preprocess import process, preprocess  # noqa
from w2v_preprocess import is_punc  # noqa

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

# read in vocab_reduced.vec file

if use_ceph:
    response = s3.get_object(
        Bucket=s3_bucket, Key=f"github-labeler/{savename}/vocab_reduced.vec"
    )
    with open("vocab_reduced.vec", "wb") as f:
        for i in response["Body"]:
            f.write(i)

with open("vocab_reduced.vec") as f:
    lines = f.readlines()
vec_size = int(lines[0].split()[1])
lines = lines[1:]
words = set([line.split()[0] for line in lines])


def in_set(word):
    """Return either the word itself or the unknown token."""
    if word in words:
        return word
    else:
        return "_unknown_"


class FtModel(FirstColFtClassifier):
    """This model is written over the skift column first classifier."""

    def __init__(self, path=""):
        """Initialize the model."""
        if not path:
            super().__init__(pretrainedVectors="vocab_reduced.vec", dim=vec_size)
        else:
            model = fasttext.load_model(path)
            setattr(self, "model", model)

    def preprocess(self, x):
        """Preprocess the text from a dataframe with processed column."""
        ret = x.title.fillna("") + " SEP " + x.body.fillna("")
        ret = ret.apply(preprocess)
        ret = ret.apply(lambda x: x.lower())
        ret = ret.apply(word_tokenize).values
        ret = [[word for word in issue if not is_punc(word)] for issue in ret]
        ret = [[in_set(w) for w in issue] for issue in ret]
        ret = [" ".join(issue) for issue in ret]
        return ret

    def fit(self, x, y):
        """Fit the model."""
        input_ = np.array(self.preprocess(x)).reshape(-1, 1)
        super().fit(input_, y)

    def predict(self, x):
        """Predict the output."""
        input_ = np.array(self.preprocess(x)).reshape(-1, 1)
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

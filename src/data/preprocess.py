"""Module that contains preprocess function called process that will process github issue text."""

import os
import boto3
from dotenv import find_dotenv, load_dotenv
from nltk.corpus import stopwords
import re
from string import punctuation
import nltk
from nltk.stem import PorterStemmer

nltk.download("stopwords")

load_dotenv(find_dotenv())

use_ceph = True

if use_ceph:
    s3_endpoint_url = os.environ["OBJECT_STORAGE_ENDPOINT_URL"]
    s3_access_key = os.environ["AWS_ACCESS_KEY_ID"]
    s3_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    s3_bucket = os.environ["OBJECT_STORAGE_BUCKET_NAME"]

    # Create an S3 client
    s3 = boto3.client(
        service_name="s3",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        endpoint_url=s3_endpoint_url,
    )

    response = s3.get_object(Bucket=s3_bucket, Key="github-labeler/wordlist.txt")
    txt = response.get("Body")
    words = []
    for i in txt:
        words += i.split(b"\n")


else:
    with open("../../wordlist.txt", "rb") as f:
        words = f.read().split(b"\n")

words = set([word.decode("utf-8") for word in words])
### preprocess functions defined below

function_list = []

pattern = r"```.+?```"
code_block_regex = re.compile(pattern, re.DOTALL)


def code_block(string):
    """Replace code blocks with a CODE_BLOCK."""
    string = re.sub(code_block_regex, "CODE_BLOCK", string)
    return string


function_list.append(code_block)

pattern = r"`{1,2}.+?`{1,2}"
inline_code_regex = re.compile(pattern, re.DOTALL)


def code_variable(string):
    """Replace inline code with VARIABLE."""
    string = re.sub(inline_code_regex, " INLINE ", string)
    return string


function_list.append(code_variable)

pattern = r"\s@[^\s]+"
tagged_user_regex = re.compile(pattern)


def tagged_user(string):
    """Replace a user tagged with USER."""
    string = re.sub(tagged_user_regex, " USER ", string)
    return string


function_list.append(tagged_user)

pattern = r"[^\s]+\.(com|org|net|gov|edu)[^\s]*"
url_regex = re.compile(pattern)


def urls(string):
    """Replace URLs with URL."""
    string = re.sub(url_regex, " URL ", string)
    return string


function_list.append(urls)

pattern = r"[\r\n]+"
enter_regex = re.compile(pattern, re.DOTALL)


def enters(string):
    """Replace newline characters with ENTER."""
    string = re.sub(enter_regex, " ", string)
    return string


function_list.append(enters)

pattern = r"#####"
bold_regex = re.compile(pattern, re.DOTALL)


def bold(string):
    """Replace bold characters with bold word."""
    string = re.sub(bold_regex, " BOLD ", string)
    return string


function_list.append(bold)


def preprocess(string):
    """Put all preprocessing functions together."""
    for func in function_list:
        string = func(string)
    return string


punct = set(punctuation)


def all_punc(word):
    """Check if a word is entirely punctuation."""
    for ch in word:
        if ch not in punct:
            return False
    return True


### process function to be imported when preprocessing

ps = PorterStemmer()

stopwds = set(stopwords.words("english"))


def process(title, body):
    """Call this function when wishing to preprocess an issue."""
    listed_words = nltk.word_tokenize(
        preprocess(
            title + " SEP " + body if type(body) == str else title + " SEP "
        ).lower()
    )
    listed_words = [word for word in listed_words if not all_punc(word)]
    stemmed = [ps.stem(word) for word in listed_words if word not in stopwds]
    ret = [word for word in stemmed if word in words]
    return ret

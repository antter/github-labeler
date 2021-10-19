"""This is a script that will house the simple preprocessing functions we use for w2v."""

import re
from string import punctuation
import langid

# simple preprocessing functions


def remove_quotes(string):
    """Remove quotes from the string (everything extracted from json has quotes."""
    if type(string) == str:
        return string[1:-1]
    else:
        return string


def is_bot(actor):
    """Identify users clearly tagged as bots."""
    if type(actor) != str:
        return True
    if actor[-5:] == "[bot]":
        return True
    else:
        return False


def is_english(text):
    """Determine if a language is English."""
    return langid.classify(text)[0] == "en"


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
    """Replace inline code with INLINE."""
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

pattern = r"[^\s]+\.(com|org|net|gov|edu|io|ai)[^\s]*"
url_regex = re.compile(pattern)


def urls(string):
    """Replace URLs with URL."""
    string = re.sub(url_regex, " URL ", string)
    return string


function_list.append(urls)

pattern = r"((\\r)*\\n)+"
enter_regex = re.compile(pattern, re.DOTALL)


def enters(string):
    """Replace newline characters with a space."""
    string = re.sub(enter_regex, " ", string)
    return string


function_list.append(enters)

pattern = r"#{3,}"
bold_regex = re.compile(pattern, re.DOTALL)


def bold(string):
    """Replace bold characters with a space."""
    string = re.sub(bold_regex, " ", string)
    return string


function_list.append(bold)


def remove_slashes(string):
    """Remove slashes."""
    return string.replace("\\", "")


function_list.append(remove_slashes)


def preprocess(string):
    """Put all preprocessing functions together."""
    for func in function_list:
        string = func(string)
    return string


# function that will remove all punctuation that is not ending a sentence or a comma


punc = set(punctuation)


def is_punc(string):
    """Check if a string is all punctuation, unless it is a sentence ender or comma."""
    if string in [".", "?", "!", ","]:
        return False
    for ch in string:
        if ch not in punc:
            return False
    return True

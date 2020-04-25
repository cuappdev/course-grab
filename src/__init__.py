"""
The Flask application package.
"""
import random
import string
from os import environ

from flask import Flask


app = Flask(__name__, static_folder="static")

app.secret_key = environ["SECRET_KEY"]
environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import src.views

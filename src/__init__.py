"""
The Flask application package.
"""
import random
import string
from os import environ

from flask import Flask
from flask_oauth import OAuth

app = Flask(__name__, static_folder='static')

app.secret_key = environ['SECRET_KEY']
oauth = OAuth()

google = oauth.remote_app(
    'google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'response_type': 'code'},
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    consumer_key="894460636145-4f5invh6pj5jb1ttg6bg79ejni1vunou.apps.googleusercontent.com",
    consumer_secret=environ['GOOGLE_CLIENT_SECRET'])

import src.views

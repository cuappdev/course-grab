"""
Routes and views for the Flask application.
"""

import bs4
import datetime
import google.oauth2.credentials
import google_auth_oauthlib.flow
from flask import render_template, request, session, redirect, url_for, flash
import json
from os import environ
import requests

from src import app

BACKEND_URL = environ.get("BACKEND_URL")

CLIENT_SECRETS_FILE = environ.get("GOOGLE_SECRETS_FILE")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def _url_for(endpoint):
    if environ.get("ENV") == "PRODUCTION":
        return url_for(endpoint, _scheme="https", _external=True)
    return url_for(endpoint, _external=True)


def create_auth_header():
    credentials = session.get("credentials")
    if credentials:
        if credentials["session_expiration"] <= round(
            datetime.datetime.now().timestamp()
        ):
            res = requests.post(
                "/api/session/update/",
                headers={"Authorization": "Bearer " + credentials["update_token"]},
            )
            serialized_session = res.json()
            session["credentials"] = serialized_session["data"]
        return {"Authorization": "Bearer " + credentials["session_token"]}
    else:
        flash("Please sign in.")


@app.route("/")
def index():
    credentials = session.get("credentials")
    course_list = []
    if credentials:
        r = requests.get(
            BACKEND_URL + "/api/users/tracking/", headers=create_auth_header()
        )
        for section in r.json()["data"]:
            title = "{} {}: {}".format(
                section["subject_code"], section["course_num"], section["title"]
            )
            course_list.append((section["catalog_num"], title, section["section"]))
    return render_template("index.html", course_list=course_list)


@app.route("/sign_in")
def sign_in():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )

    flow.redirect_uri = _url_for("oauth2callback")

    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    session["state"] = state

    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    state = session["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = _url_for("oauth2callback")

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    id_token = flow.credentials.id_token
    res = requests.post(
        BACKEND_URL + "/api/session/initialize/", json={"token": id_token}
    )
    serialized_session = res.json()
    if serialized_session["success"]:
        session["credentials"] = serialized_session["data"]
        return redirect(_url_for("index"))
    else:
        flash(serialized_session["data"]["errors"][0])


@app.route("/submitted", methods=["POST"])
def submit_request():
    if session.get("credentials") is None:
        flash("Please sign in first.")
    else:
        r = requests.get(
            BACKEND_URL + "/api/users/tracking/", headers=create_auth_header()
        )
        if len(r.json()["data"]) == 3:
            flash("You cannot track more than three courses at a time.")
        else:
            course_code = request.form["course_number"]
            res = requests.post(
                BACKEND_URL + "/api/sections/track/",
                json={"course_id": course_code},
                headers=create_auth_header(),
            )
            if not res.json()["success"]:
                flash(res.json()["data"]["errors"][0])
    return redirect(_url_for("index"))


@app.route("/remove/<int:course_num>", methods=["POST"])
def remove(course_num):
    if session.get("credentials") is None:
        flash("Your session has expired. Please sign in again.")
    else:
        res = requests.post(
            BACKEND_URL + "/api/sections/untrack/",
            json={"course_id": course_num},
            headers=create_auth_header(),
        )
    return redirect(_url_for("index"))


@app.route("/sign_out")
def sign_out():
    if "credentials" in session:
        del session["credentials"]
    return redirect(_url_for("index"))


@app.errorhandler(400)
def bad_request(e):
    return "400 error", 400


@app.errorhandler(404)
def page_not_found(e):
    return "404 error", 404


@app.errorhandler(500)
def internal_server_error(e):
    return (
        "Looks like you ran into a bug! Turns out making a website is kind of hard. We will fix this someday but in the meantime, just <a href='https://coursegrab.cornellappdev.com'>click here</a> to return to the main page. Refreshing the page almost always fixes the problem.",
        500,
    )

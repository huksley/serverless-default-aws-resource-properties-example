"""myproject web application"""

import http.client
import os
import re

import logging
import requests

from flask import Flask, redirect, render_template, send_from_directory, request, url_for, session, Response
from flask_caching import Cache



def dev():
    """Detect dev environment"""
    return os.environ.get("AWS_EXECUTION_ENV") is None


app = Flask(__name__)

app.secret_key = os.environ['FLASK_SECRET_KEY']

cacheConfig = {
    "CACHE_TYPE": "simple" if dev() else "simple",
    "CACHE_DEFAULT_TIMEOUT": 300
}

if dev() and False:
    http.client.HTTPConnection.debuglevel = 1

app.config.from_mapping(cacheConfig)
cache = Cache(app)

logging.basicConfig(level=logging.INFO)
if not dev():
    logging.getLogger("werkzeug").setLevel(logging.WARN)

if dev():
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@cache.memoize(timeout = 60)
def web(query_string, host):
    resp = Response("Hello world")
    resp.headers['Strict-Transport-Security'] = 'max-age=63072000'  # 2 years
    return resp

@app.route("/")
def root():
    """Root page"""
    host = request.headers['Host']
    logger.info("Host: %s remote %s", host, request.remote_addr)
    if re.match(r'^www\.', host):
        return redirect("http://" + re.sub(r'^www\.', "", host), 301)
    return web(request.query_string, host)


@app.route("/favicon.ico")
def favicon():
    """Redirect to proper favicon"""
    return redirect("static/icon.svg", code=302)


@app.route('/robots.txt')
@app.route('/site.webmanifest')
def static_from_root():
    """Mapping for static files"""
    return send_from_directory(app.static_folder, request.path[1:])


@app.route("/index.html")
def index():
    """Old root page"""
    return redirect(".", 302)


def get_app():
    """Get app instance"""
    return app

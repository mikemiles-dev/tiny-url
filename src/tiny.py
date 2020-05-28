from flask import Flask, request, redirect, render_template
import logging
import json
import os
import redis
import myrust_shortener
import urllib

from src import redis_wrapper, validators

app = Flask(__name__,  template_folder='templates')

INCREMENT_KEY = "SHORTENER_INDEX"

FORMATTER = logging.Formatter('%(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s')
# console handler
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.INFO)
CONSOLE_HANDLER.setFormatter(FORMATTER)
log = logging.getLogger(__name__)
log.addHandler(CONSOLE_HANDLER)
log.setLevel(logging.INFO)


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 Message"""
    return json.dumps({"error": "not found"}), 404


@app.route('/')
def index():
    """Main Index Route"""
    return render_template('index.html')


@app.route('/<key>/', methods=["GET"])
def lookup(key):
    """URL to resolve short link to link

    Simple try and fetch if short link exists
    or error.
    Always returns json string
    """
    try:
        rdb = redis_wrapper.new_redis_connection()
    except redis.exceptions.ConnectionError:
        return json.dumps({"error": "redis down"})
    try:
        url = rdb.get(key)
    except (ConnectionError, TimeoutError):
        return json.dumps({"error": "redis server error, contact admin"})
    if url is None:
        return json.dumps({"error": "Invalid key"})
    if validators.validate_url(url.decode()) is not None:
        return redirect(validators.validate_redirect(url))
    return json.dumps({"error": "Invalid url"})


@app.route('/add/', methods=["POST"])
def add_encoded():
    """URL to add new short links

    Pass key as part of URL.  Runs some validation.
    If custom short link provided we see if it exists.
    If not custom short link we run our shortener code.
    If so we return an error otherwise we create.
    Always returns json string
    """
    url = request.form.get('url')
    custom = request.form.get('custom')
    if url is None:
        return json.dumps({"error": "url not provided"})
    if validators.validate_url(url) is None:
        return json.dumps({"error": "url not provided"})
    try:
        rdb = redis_wrapper.new_redis_connection()
    except redis.exceptions.ConnectionError:
        return json.dumps({"error": "redis down"})
    if custom is None:
        try:
            shorten_inc = rdb.incr(INCREMENT_KEY)
        except (ConnectionError, TimeoutError):
            return json.dumps({"error":
                               "redis server error, contact admin"})
        try:
            link_key = myrust_shortener.shorten(shorten_inc)
        except Exception as shortener_error:
            log.error(shortener_error)
            return json.dumps({"error": "Unknown error, contact admin"})
    else:
        try:
            custom_lookup = rdb.get(custom)
        except (ConnectionError, TimeoutError):
            return json.dumps({"error":
                               "redis server error, contact admin"})
        if custom_lookup is not None:
            return json.dumps({"error": "Custom short link exists"})
        link_key = custom
    try:
        rdb.set(link_key, url)
    except (ConnectionError, TimeoutError):
        return json.dumps({"error": "redis server error, contact admin"})
    link_url = urllib.parse.urljoin(os.getenv("DOMAIN_NAME"), link_key)
    return json.dumps({"status": "success", "url": link_url}), 200

from flask import Flask, request, redirect, render_template
from datetime import datetime
import logging
import json
import os
import myrust_shortener
import urllib

from src.redis_wrapper import redis_connect
from src import validators

app = Flask(__name__,  template_folder='templates')

INCREMENT_KEY = "SHORTENER_INDEX"
DT_FMT = "%Y/%m/%d %H:%M:%S"

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
    rdb = redis_connect()
    if rdb is None:
        return json.dumps({"error": "redis down"})
    try:
        url = rdb.get(key)
        stats = rdb.get(f"stats-{key}")
    except (ConnectionError, TimeoutError) as redis_timeout:
        log.error(redis_timeout)
        return json.dumps({"error": "redis server error, contact admin"})
    if url is None:
        return json.dumps({"error": "Invalid key"})
    if validators.validate_url(url.decode()) is not None:
        if stats is not None:
            stats = json.loads(stats)
            stats["visits"] += 1
            try:
                rdb.set(f"stats-{key}", json.dumps(stats))
            except (ConnectionError, TimeoutError) as stats_error:
                log.error(stats_error)
                return json.dumps({"error":
                                   "redis server error, contact admin"})
        return redirect(validators.validate_redirect(url))
    return json.dumps({"error": "Invalid url"})


@app.route('/stats/<key>/', methods=["GET"])
def stats(key):
    rdb = redis_connect()
    if rdb is None:
        return json.dumps({"error": "redis down"})
    stats_key = f"stats-{key}"
    try:
        stats = rdb.get(stats_key)
    except (ConnectionError, TimeoutError) as redis_error:
        log.error(redis_error)
        return json.dumps({"error": "redis server error, contact admin"})
    if stats is None:
        return json.dumps({"error": "No stats"})
    stats = json.loads(stats)
    dt_created = datetime.strptime(stats["created"], DT_FMT)
    diff_dt = (datetime.utcnow() - dt_created).days + 1
    stats["average_visits_per_day"] = stats["visits"] / diff_dt
    return json.dumps(stats)


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
    if url is None and validators.validate_url(url) is None:
        return json.dumps({"error": "url not provided"})
    rdb = redis_connect()
    if rdb is None:
        return json.dumps({"error": "redis down"})
    if custom is None:
        try:
            shorten_inc = rdb.incr(INCREMENT_KEY)
        except (ConnectionError, TimeoutError) as redis_inc_error:
            log.error(redis_inc_error)
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
    stats_key = f"stats-{link_key}"
    stats_data = json.dumps({"created": datetime.utcnow().strftime(DT_FMT),
                             "visits": 0})
    try:
        rdb.set(link_key, url)
        rdb.set(stats_key, stats_data)
    except (ConnectionError, TimeoutError) as stats_error:
        log.error(stats_error)
        return json.dumps({"error": "redis server error, contact admin"})

    link_url = urllib.parse.urljoin(os.getenv("DOMAIN_NAME"), link_key)
    stats_url = urllib.parse.urljoin(os.getenv("DOMAIN_NAME"),
                                     "stats/" + link_key)
    return json.dumps({"status": "success",
                       "stats_url": stats_url,
                       "url": link_url}), 200

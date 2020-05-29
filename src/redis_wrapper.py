import logging
import redis
import time
import signal
import sys
import os


FORMATTER = logging.Formatter('%(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s')

log = logging.getLogger(__name__)


class GracefulKiller:
    """Class to assist in signal shutdown with redis pool"""

    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


def redis_connect():
    """Attempts a redis connection"""
    try:
        return new_redis_connection()
    except redis.exceptions.ConnectionError as redis_error:
        log.error(redis_error)
        return None


def new_redis_connection():
    """Returns redis connection"""

    redis_url = os.getenv("REDIS_HOST")
    log.info("Connecting to redis: %s", redis_url)
    redis_pool = redis.connection.ConnectionPool.from_url(redis_url)
    rdb = redis.Redis(connection_pool=redis_pool)
    count = 0
    max_retries = 5
    while count < max_retries:
        if GracefulKiller.kill_now:
            sys.exit(1)

        try:
            if rdb.ping():
                return rdb
        except redis.exceptions.ConnectionError as redis_error:
            log.error(redis_error)
        log.error("Cannot connect to redis, retrying...")
        time.sleep(5)
        count = count + 1
    raise redis.exceptions.ConnectionError

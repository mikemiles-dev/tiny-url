import logging
import redis
import time
from src.helpers import GracefulKiller
import sys
import os


FORMATTER = logging.Formatter('%(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s')
# console handler
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.INFO)
CONSOLE_HANDLER.setFormatter(FORMATTER)
log = logging.getLogger(__name__)
log.addHandler(CONSOLE_HANDLER)
log.setLevel(logging.INFO)


def new_redis_connection():
    """Returns redis connection"""

    _killer = GracefulKiller

    redis_url = os.getenv("REDIS_HOST")
    log.info("Connecting to redis: %s", redis_url)
    redis_pool = redis.connection.ConnectionPool.from_url(redis_url)
    rdb = redis.Redis(connection_pool=redis_pool)
    count = 0
    max_retries = 5
    while count < max_retries:
        if _killer.kill_now:
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

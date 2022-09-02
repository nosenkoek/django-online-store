import backoff

from redis import StrictRedis, RedisError
from contextlib import contextmanager

REDIS_HOST = 'localhost'
REDIS_PORT = 6379


@backoff.on_exception(backoff.expo, RedisError, max_tries=5)
@contextmanager
def redis_connection():
    conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                       charset="utf-8", decode_responses=True,
                       socket_timeout=5)
    try:
        conn.ping()
    except TimeoutError:
        raise RedisError('Error connection to Redis')

    yield conn
    conn.connection_pool.disconnect()

import redis

from contextlib import contextmanager

REDIS_HOST = 'localhost'
REDIS_PORT = 6379


@contextmanager
def redis_connection():
    conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                             charset="utf-8", decode_responses=True)
    yield conn
    conn.connection_pool.disconnect()
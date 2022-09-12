import backoff

from elasticsearch import Elasticsearch, ElasticsearchException
from redis import StrictRedis, RedisError
from contextlib import contextmanager

# REDIS_HOST = 'localhost'
REDIS_HOST = 'redis'
REDIS_PORT = 6379

# ES_HOST = 'localhost'
ES_HOST = 'es'
ES_PORT = 9200


@backoff.on_exception(backoff.expo, RedisError, max_tries=5)
@contextmanager
def redis_connection():
    conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                       charset="utf-8", decode_responses=True,
                       socket_timeout=3)
    try:
        conn.ping()
    except TimeoutError:
        raise RedisError('Error connection to Redis')

    yield conn
    conn.connection_pool.disconnect()


@backoff.on_exception(backoff.expo, ElasticsearchException, max_tries=5)
@contextmanager
def es_connection() -> Elasticsearch:
    try:
        conn = Elasticsearch(f'http://{ES_HOST}:{ES_PORT}')
    except ElasticsearchException:
        raise ElasticsearchException('Error elastic connection')

    if not conn.ping():
        raise ElasticsearchException('Error elastic connection')

    yield conn
    conn.close()

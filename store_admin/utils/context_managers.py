import backoff

from django.conf import settings

from elasticsearch import Elasticsearch, ElasticsearchException
from redis import StrictRedis, RedisError
from contextlib import contextmanager


@backoff.on_exception(backoff.expo, RedisError, max_tries=5)
@contextmanager
def redis_connection():
    conn = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
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
        conn = Elasticsearch(f'http://{settings.ES_HOST}:{settings.ES_PORT}')
    except ElasticsearchException:
        raise ElasticsearchException('Error elastic connection')

    if not conn.ping():
        raise ElasticsearchException('Error elastic connection')

    yield conn
    conn.close()

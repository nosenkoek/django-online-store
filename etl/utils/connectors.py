# todo: pg_conn, es_conn (context manager + backoff)
#  Factory -> pg_conn, es_conn -> yield conn
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Callable

from etl.utils.settings import DSN, REDIS_HOST, REDIS_PORT, ES_PORT, ES_HOST
from psycopg2 import connect, OperationalError, Error
from redis import StrictRedis, RedisError
from redis.exceptions import TimeoutError
from elasticsearch import Elasticsearch, ElasticsearchException


class BaseConnection(ABC):
    """Абстрактный класс задающий интерфейс для элементов фабрики"""
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class PostgresConnection(BaseConnection):
    """Подключение к БД postgresql"""
    @contextmanager
    def __call__(self) -> connect:
        try:
            conn = connect(**DSN)
        except OperationalError:
            raise Error('Error connect to PostgreSQL')

        if not conn.status:
            raise Error('Error connect to PostgreSQL')
        yield conn
        conn.close()


class RedisConnection(BaseConnection):
    """Подключение к Redis"""
    @contextmanager
    def __call__(self) -> StrictRedis:
        conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                           charset="utf-8", decode_responses=True,
                           socket_timeout=5)
        try:
            conn.ping()
        except TimeoutError:
            raise RedisError('Error connection to Redis')

        yield conn
        conn.connection_pool.disconnect()


class ElasticConnection(BaseConnection):
    """Подключение к ElasticSearch"""
    @contextmanager
    def __call__(self) -> Elasticsearch:
        try:
            conn = Elasticsearch(f'http://{ES_HOST}:{ES_PORT}')
        except ElasticsearchException:
            raise ElasticsearchException

        if not conn.ping():
            raise ElasticsearchException('Error elastic connection')

        yield conn
        conn.close()


class FactoryConnection():
    """Фабрика объектов для подключения"""
    _CONNECTIONS = {
        'pg': PostgresConnection(),
        'redis': RedisConnection(),
        'es': ElasticConnection()
    }

    def get_connection(self, key: str) -> Callable:
        """
        Возвращает генератор подключения для использования контекст менеджера.
        :param key: ключ объекта для подключения,
        :return: генератор подключения
        """
        return self._CONNECTIONS.get(key).__call__

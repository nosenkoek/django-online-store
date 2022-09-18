import backoff

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Callable

from psycopg2 import connect as pg_connect, OperationalError, Error as PG_Error
from redis import StrictRedis, RedisError
from redis.exceptions import TimeoutError
from elasticsearch import Elasticsearch, ElasticsearchException

from settings import DSN, REDIS_HOST, REDIS_PORT, ES_PORT, ES_HOST
from utils.logger import ETLLogger

logger = ETLLogger().get_logger()


class BaseConnection(ABC):
    """Абстрактный класс задающий интерфейс для элементов фабрики"""
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class PostgresConnection(BaseConnection):
    """Подключение к БД postgresql"""
    @backoff.on_exception(backoff.expo, PG_Error, max_tries=5)
    @contextmanager
    def __call__(self) -> pg_connect:
        try:
            conn = pg_connect(**DSN)
        except OperationalError as err:
            logger.error(f'not connect to database | {err}')
            raise PG_Error('Error connect to PostgreSQL')

        if not conn.status:
            logger.error('database not responding')
            raise PG_Error('Error connect to PostgreSQL')
        yield conn
        conn.close()


class RedisConnection(BaseConnection):
    """Подключение к Redis"""
    @backoff.on_exception(backoff.expo, RedisError, max_tries=5)
    @contextmanager
    def __call__(self) -> StrictRedis:
        conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                           charset="utf-8", decode_responses=True,
                           socket_timeout=5)
        try:
            conn.ping()
        except TimeoutError:
            logger.error('redis not responding')
            raise RedisError('Error connection to Redis')

        yield conn
        conn.connection_pool.disconnect()


class ElasticConnection(BaseConnection):
    """Подключение к ElasticSearch"""
    @backoff.on_exception(backoff.expo, ElasticsearchException, max_tries=5)
    @contextmanager
    def __call__(self) -> Elasticsearch:
        try:
            conn = Elasticsearch(f'http://{ES_HOST}:{ES_PORT}')
        except ElasticsearchException as err:
            logger.error(f'not connect to elasticsearch | {err}')
            raise ElasticsearchException

        if not conn.ping():
            logger.error('elasticsearch not responding')
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

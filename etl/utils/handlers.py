from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable

from elasticsearch.helpers import streaming_bulk

from utils.connectors import FactoryConnection
from utils.logger import ETLLogger

from settings import COUNT_ROW_IN_PACKAGE

logger = ETLLogger().get_logger()


class BaseHandler(ABC):
    """Абстрактный класс для работы с разными БД"""
    @abstractmethod
    def get_data(self, *args, **kwargs):
        pass

    @abstractmethod
    def load_data(self, *args, **kwargs):
        pass


class RedisHandler(BaseHandler):
    """Обработчик загрузки/выгрузки данных из Redis"""
    def __init__(self):
        self._conn = FactoryConnection().get_connection('redis')

    def get_data(self) -> str:
        """
        Получение информации из Redis о последнем обновлении elastic
        :return: дата и время последнего обновления elastic
        """
        with self._conn() as redis_conn:
            pg_updated_at = redis_conn.get('pg_updated_at')
        logger.info(f'last migrate to es {pg_updated_at}')
        return pg_updated_at

    def load_data(self):
        """
        Загрузка даты и времени обновления elastic
        """
        with self._conn() as redis_conn:
            redis_conn.set('pg_updated_at', str(datetime.now()))
        logger.info('time last migration updated')


class PostgresHandler(BaseHandler):
    """Обработчик загрузки/выгрузки данных из PostgreSQL"""
    def __init__(self):
        self._conn = FactoryConnection().get_connection('pg')

    def get_data(self, pg_updated_at) -> list[tuple[str]]:
        """
        Генератор. Получение пакета данных запроса из БД
        :param pg_updated_at: дата и время последнего обновления elastic
        :return: список с данными для загрузки в elastic
        """
        query = 'SELECT p.product_id, c.name, p.name, p.description, m.name ' \
                'FROM product p ' \
                'JOIN category c ON c.category_id = p.category_fk ' \
                'JOIN manufacturer m ' \
                'ON p.manufacturer_fk = m.manufacturer_id '\
                'WHERE p.updated > %s OR c.updated > %s OR m.updated > %s;'

        with self._conn() as pg_conn, pg_conn.cursor() as cur:
            cur.execute(query, (pg_updated_at, pg_updated_at, pg_updated_at))
            data_fetchmany = cur.fetchmany(COUNT_ROW_IN_PACKAGE)
            data = (item for item in data_fetchmany)

            while data_fetchmany:
                yield data
                data_fetchmany = cur.fetchmany(COUNT_ROW_IN_PACKAGE)
                data = (item for item in data_fetchmany)

        logger.info('data received from database')

    def load_data(self, *args, **kwargs):
        pass


class ElasticHandler(BaseHandler):
    """Обработчик загрузки/выгрузки данных из Elasticsearch"""
    def __init__(self):
        self._conn = FactoryConnection().get_connection('es')

    def get_data(self):
        pass

    def load_data(self, es_data: str) -> None:
        """
        Загрузка данных в Elastic
        :param es_data: данные в формате json
        """
        with self._conn() as es_conn:
            def gen_data():
                for line in es_data:
                    yield line

            result = streaming_bulk(es_conn, gen_data())

            for item in result:
                if not item[1]:
                    logger.warning(f"error load doc {item[2]['_id']}")
        logger.info('package data loaded to elasticsearch')


class ETLObjectFactory():
    """Класс-фабрика составляющих ETL"""
    def __init__(self):
        self._ETL_OBJECT = {
            'redis': RedisHandler(),
            'pg': PostgresHandler(),
            'es': ElasticHandler()
        }

    def get_etl_object(self, key: str) -> BaseHandler:
        """
        Возвращает обработчик составляющих ETL
        :param key: ключ обработчика ('redis', 'pg, 'es')
        :return:
        """
        result = self._ETL_OBJECT.get(key)
        return result


class ETLHandler():
    """Внешний интерфейс для взаимодействия с объектами составляющие ETL"""
    def __init__(self):
        self._etl_object_factory = ETLObjectFactory()

    def get_pg_updated_at(self) -> str:
        """
        Получение даты и времени из Redis последней миграции данных.
        :return: дата и время
        """
        pg_updated_at = self._etl_object_factory\
            .get_etl_object('redis').get_data()
        return pg_updated_at

    def load_pg_updated_at(self):
        """Запись даты и времени выполненной миграции"""
        self._etl_object_factory.get_etl_object('redis').load_data()

    def get_pg_data(self, pg_updated_at: str) -> Iterable:
        """Генератор для получения пакета данных из БД"""
        pg_data = self._etl_object_factory\
            .get_etl_object('pg').get_data(pg_updated_at)
        return pg_data

    def load_es_data(self, es_data):
        """Запись данных в ES"""
        self._etl_object_factory\
            .get_etl_object('es').load_data(es_data)

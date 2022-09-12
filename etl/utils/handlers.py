from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable

from elasticsearch.helpers import streaming_bulk

from utils.connectors import FactoryConnection
from utils.logger import ETLLogger

from settings import COUNT_ROW_IN_PACKAGE

logger = ETLLogger().get_logger()


class BaseHandler(ABC):
    """Абстрактный класс для работы с разными БД"""
    def __init__(self, key: str) -> None:
        self._conn = FactoryConnection().get_connection(key)

    @abstractmethod
    def get_data(self, *args, **kwargs):
        pass

    @abstractmethod
    def load_data(self, *args, **kwargs):
        pass


class RedisHandler(BaseHandler):
    """Стратегия взаимодействия с Redis"""
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
            redis_conn.set('pg_updated_at', datetime.now())
        logger.info('time last migration updated')


class PostgresHandler(BaseHandler):
    """Стратегия взаимодействия с PostgreSQL"""
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
            data = [item for item in cur.fetchmany(COUNT_ROW_IN_PACKAGE)]

            while data:
                yield data
                data = [item for item in cur.fetchmany(COUNT_ROW_IN_PACKAGE)]

        logger.info('data received from database')

    def load_data(self, *args, **kwargs):
        pass


class ElasticHandler(BaseHandler):
    """Стратегия взаимодействия с Elasticsearch"""
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
        logger.info('data loaded to elasticsearch')


class ETLObject():
    """Класс составляющих ETL"""
    def __init__(self, strategy: BaseHandler):
        self.strategy = strategy

    def get_data(self, *args, **kwargs):
        result = self.strategy.get_data(*args, **kwargs)
        return result

    def load_data(self, *args, **kwargs):
        self.strategy.load_data(*args, **kwargs)


class ETLHandler():
    """Внешний интерфейс для взаимодействия с объектами составляющие ETL"""
    def __init__(self):
        self._redis_handler = RedisHandler('redis')
        self._pg_handler = PostgresHandler('pg')
        self._es_handler = ElasticHandler('es')

        self._STRATEGY = {
            'redis': ETLObject(self._redis_handler),
            'pg': ETLObject(self._pg_handler),
            'es': ETLObject(self._es_handler)
        }

    def get_pg_updated_at(self) -> str:
        """
        Получение даты и времени из Redis последней миграции данных.
        :return: дата и время
        """
        pg_updated_at = self._STRATEGY.get('redis').get_data()
        return pg_updated_at

    def load_pg_updated_at(self):
        """Запись даты и времени выполненной миграции"""
        self._STRATEGY.get('redis').load_data()

    def get_pg_data(self, pg_updated_at) -> Callable:
        """Генератор для получения пакета данных из БД"""
        pg_data = self._STRATEGY.get('pg').get_data(pg_updated_at)
        return pg_data

    def load_es_data(self, es_data, *args, **kwargs):
        """Запись данных в ES"""
        self._STRATEGY.get('es').load_data(es_data, *args, **kwargs)

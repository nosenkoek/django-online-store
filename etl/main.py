from typing import Type

from utils.handlers import ETLHandler
from utils.pg_es_adapter import PgEsAdapter
from utils.logger import ETLLogger

logger = ETLLogger().get_logger()


class ETL():
    """
    Фасад, реализующий миграцию данных из БД в Elasticsearch
    Args:
        handler: класс обработчик данных объектов миграции,
        adapter: класс адаптер, трансформирующий данные из БД в elasticsearch
    """

    def __init__(self, handler: Type[ETLHandler], adapter: Type[PgEsAdapter]):
        self.handler_cls = handler
        self.adapter_cls = adapter

    def pg_es_migrate(self) -> None:
        """
        Миграция данных из БД в elasticsearch
        """
        handler = self.handler_cls()
        pg_updated_at = handler.get_pg_updated_at()

        for pg_data in handler.get_pg_data(pg_updated_at):
            adapter = self.adapter_cls(pg_data)
            data = adapter.get_dict_for_load()
            handler.load_es_data(data)
        else:
            logger.warning("don't data for migration")

        handler.load_pg_updated_at()
        logger.info('data migration done')


if __name__ == '__main__':
    etl = ETL(ETLHandler, PgEsAdapter)
    etl.pg_es_migrate()

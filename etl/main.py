from typing import Type

from utils.handlers import ETLHandler
from utils.pg_es_adapter import PackageDataPG, PackageDataAdapter
from utils.logger import ETLLogger

logger = ETLLogger().get_logger()


class ETL():
    """
    Фасад, реализующий миграцию данных из БД в Elasticsearch
    Args:
        handler_cls: класс обработчик данных объектов миграции,
        pg_data_cls: класс с пакетами данных из PG
        adapter_cls: класс адаптер, трансформирующий данные из БД в ES
    """

    def __init__(self, handler_cls: Type[ETLHandler],
                 pg_data_cls: Type[PackageDataPG],
                 adapter_cls: Type[PackageDataAdapter]):
        self._handler_cls = handler_cls
        self._pg_data_cls = pg_data_cls
        self._adapter_cls = adapter_cls

    def pg_es_migrate(self) -> None:
        """
        Миграция данных из БД в elasticsearch
        """
        handler = self._handler_cls()
        pg_updated_at = handler.get_pg_updated_at()
        flag_data_has = False

        for pg_data in handler.get_pg_data(pg_updated_at):
            es_data_cls = self._adapter_cls(self._pg_data_cls(pg_data))
            data = es_data_cls.get_data()
            handler.load_es_data(data)
            flag_data_has = True

        if not flag_data_has:
            logger.warning("no data for migration")

        handler.load_pg_updated_at()
        logger.info('data migration done')


if __name__ == '__main__':
    etl = ETL(ETLHandler, PackageDataPG, PackageDataAdapter)
    etl.pg_es_migrate()

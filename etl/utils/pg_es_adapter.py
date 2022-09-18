from abc import abstractmethod, ABC
from typing import List, Iterable, Dict
from uuid import UUID

from pydantic import BaseModel, StrictStr

from settings import ES_FIELDS


class ProductEs(BaseModel):
    """Модель для валидации данных из БД"""
    product_id: UUID
    category: StrictStr
    name: StrictStr
    description: StrictStr
    manufacturer: StrictStr


class BaseData(ABC):
    @abstractmethod
    def get_data(self):
        pass


class PackageDataPG(BaseData):
    """
    Объект пакета данных из PostgreSQL
    Args:
        pg_data: генератор с пакетом данных
    """
    def __init__(self, pg_data: Iterable):
        self._pg_data = pg_data

    def get_data(self):
        """
        Возвращает пакет данных из PG.
        :return: генератор с пакетом данных
        """
        return self._pg_data


class PackageDataAdapter(BaseData):
    """
    Адаптер для пакета данных из PG в ES
    Args:
        data_object: объект с пакетом данных из PG
    """
    def __init__(self, data_object: PackageDataPG):
        self._data_object = data_object

    def _create_model(self) -> List[ProductEs]:
        """
        Создания модели pydantic и валидация данных.
        :return: список с моделями
        """
        data_dict = [dict(zip(ES_FIELDS, line))
                     for line in self._data_object.get_data()]
        products = [ProductEs(**item) for item in data_dict]
        return products

    def get_data(self) -> List[Dict[str, str]]:
        """
        Возвращает пакет данных для ES.
        :return: словарь с данными для загрузки в ES
        """
        es_data = [product.dict() for product in self._create_model()]

        for item in es_data:
            item.update({'_index': 'products', '_id': item['product_id']})
        return es_data

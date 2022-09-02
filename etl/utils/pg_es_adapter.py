from typing import List, Dict, Tuple
from uuid import UUID

from pydantic import BaseModel, StrictStr


class ProductEs(BaseModel):
    """Модель для валидации данных из БД"""
    product_id: UUID
    category: StrictStr
    name: StrictStr
    description: StrictStr
    manufacturer: StrictStr


class PgEsAdapter():
    """
    Адаптер, трансформирующий данные из БД в elasticsearch
    Args:
        pg_data: данные из БД
    """
    def __init__(self, pg_data: List[Tuple[str]]):
        self.pg_data = pg_data
        self.fields = ['product_id', 'category', 'name',
                       'description', 'manufacturer']

    def _transform_to_dict(self) -> List[Dict[str, str]]:
        """
        Перевод данные из кортежа в словарь, для создания модели.
        :return: список со словарями с данными
        """
        data = [dict(zip(self.fields, line)) for line in self.pg_data]
        return data

    def _create_model(self) -> List[ProductEs]:
        """
        Создания модели pydantic и валидация данных.
        :return: список с моделями
        """
        data = self._transform_to_dict()
        products = [ProductEs(**item) for item in data]
        return products

    def get_dict_for_load(self) -> List[Dict[str, str]]:
        """
        Получение конечного списка со словарями для загрузки в elasticsearch
        :return: список со словарями для загрузки в elasticsearch
        """
        dict_list = [product.dict()
                     for product in self._create_model()]

        for item in dict_list:
            item.update({'_index': 'products', '_id': item['product_id']})
        return dict_list

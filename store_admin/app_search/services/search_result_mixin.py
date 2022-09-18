from typing import List
from elasticsearch_dsl import Search

from utils.context_managers import es_connection


class SearchResultMixin():
    """Миксин для поиска по elasticsearch"""
    @staticmethod
    def search_match(query: str) -> List[str]:
        """
        Поиск товаров по запросу пользователя.
        :param query: строка запроса на поиск от пользователя,
        :return: список product_id по совпадению
        """
        with es_connection() as es_conn:
            search = Search(using=es_conn).query(
                'multi_match',
                query=query,
                fields=['category^2', 'name^2', 'description', 'manufacturer']
            )[:100]
            response = search.execute()

        res_product_ids = [hit.product_id for hit in response]
        return res_product_ids

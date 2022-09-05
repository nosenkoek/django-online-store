from datetime import timedelta, datetime

from functools import wraps
from typing import Callable

from app_products.models import Product
from utils.context_managers import redis_connection

NAME_ATRS_CACHE = {
    '127.0.0.1:8000': ['count_views', 'popular_product_ids'],
    'testserver': ['count_views_test', 'popular_product_ids_test'],
}

SECONDS_CACHE = 10


class StrategyBase():
    """Интерфейс стратегии"""
    def cache_views_product(self, product: Product, redis_conn) -> None:
        """
        Добавляет в кэш редиса хэш таблицу просмотренных товаров.
        :param product: просмотренный товар
        """
        if redis_conn.exists(self.count_views) and redis_conn.hexists(
                self.count_views, str(product.product_id)):

            count_views = redis_conn.hget(self.count_views,
                                          str(product.product_id))
            redis_conn.hset(self.count_views,
                            str(product.product_id),
                            int(count_views) + 1)
        else:
            redis_conn.hset(self.count_views, str(product.product_id), 1)

    def cache_popular_product(self, redis_conn):
        """Добавляет в кэш редиса список с популярными товарами"""
        redis_conn.delete(self.popular_product_ids)

        data = redis_conn.hgetall(self.count_views)
        popular_product_ids = sorted(data,
                                     key=lambda key: int(data.get(key)),
                                     reverse=True)[:16]
        redis_conn.rpush(self.popular_product_ids, *popular_product_ids)


class WorkCache(StrategyBase):
    """Стратегия режима работы"""
    def __init__(self):
        self.count_views = NAME_ATRS_CACHE.get('127.0.0.1:8000')[0]
        self.popular_product_ids = NAME_ATRS_CACHE.get('127.0.0.1:8000')[1]


class TestCache(StrategyBase):
    """Стратегия для тестов"""
    def __init__(self):
        self.count_views = NAME_ATRS_CACHE.get('testserver')[0]
        self.popular_product_ids = NAME_ATRS_CACHE.get('testserver')[1]

# todo: добавить еще одну стратегию, когда отвалился редис


class CachePopularProduct():
    """
    Объект выполнения кэширования исходя из стратегии
    Args:
        strategy: выбор стратегии
    """
    def __init__(self, strategy: StrategyBase) -> None:
        self._strategy = strategy

    def __call__(self, product: Product, func: Callable) -> None:
        with redis_connection() as redis_conn:
            self._strategy.cache_views_product(product, redis_conn)

            if datetime.utcnow() >= func.expiration:
                self._strategy.cache_popular_product(redis_conn)
                func.expiration = datetime.utcnow() + func.cache_time


class CachePopularProductHandler():
    """Внешний интерфейс взаимодействия с кэшом популярных товаров в Redis"""
    def __init__(self):
        self._test_cache = TestCache()
        self._work_cache = WorkCache()
        self._STRATEGY = {
            'testserver': CachePopularProduct(self._test_cache),
            '127.0.0.1:8000': CachePopularProduct(self._work_cache)
        }

    def __call__(self, host, product, func):
        self._STRATEGY.get(host).__call__(product, func)


def cache_popular_product(func: Callable) -> Callable:
    """ Декоратор для получения списка популярных товаров
    (из кол-ва просмотров)"""
    func.cache_time = timedelta(seconds=SECONDS_CACHE)
    func.expiration = datetime.utcnow() + func.cache_time

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        product = args[0].get_object()
        host = args[1].get_host()

        cache_handler = CachePopularProductHandler()
        cache_handler.__call__(host, product, func)
        return result
    return wrapper

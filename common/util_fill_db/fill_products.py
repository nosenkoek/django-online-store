import random
import uuid
from abc import ABC
from dataclasses import dataclass

from datetime import datetime
from typing import List, Dict

import psycopg2
from faker import Faker
from psycopg2.extras import execute_batch
from psycopg2.extensions import cursor

from common.util_fill_db.settings import MANUFACTURERS_COUNT, PAGE_SIZE, \
    PRODUCTS_IN_CATEGORY_COUNT, PRODUCTS_LIMITED_COUNT, IMAGE_LINKS, \
    FEATURES_VALUE, FEATURES_GROUP_TEXT, DSN


@dataclass
class CategoryData():
    """Объект с загруженными данными из БД"""
    category_ids: List[str]
    category_feature: Dict[str, List[str]]
    feature_id_checkbox: List[str]
    feature_id_name_select: Dict[str, str]


class Builder(ABC):
    pass


class DownloadDataBuilder(Builder):
    """
    Класс строитель для загрузки данных из БД
    Args:
        cur: курсор подключения к postgres
    """
    def __init__(self, cur: cursor) -> None:
        self.cur = cur
        self.category_ids, self.feature_id_checkbox = [], []
        self.category_feature, self.feature_id_name_select = {}, {}

    def download_category_ids(self) -> None:
        """Загрузка списка category_id"""
        query = 'SELECT category_id FROM category WHERE level=1 ' \
                'ORDER BY category_id;'
        self.cur.execute(query)
        self.category_ids = [category_id[0] for category_id in self.cur]

    def download_category_feature(self) -> None:
        """Загрузка словаря соответствия category_id и feature_id"""
        for category_id in self.category_ids:
            query = 'SELECT feature_fk FROM category_feature ' \
                    'WHERE category_fk = %s;'
            self.cur.execute(query, (category_id,))
            self.category_feature.update(
                {category_id: [feature_id[0] for feature_id in self.cur]}
            )

    def download_feature_id_checkbox(self) -> None:
        """Загрузка списка feature_id у которых тип checkbox"""
        query = "SELECT feature_id FROM feature " \
                "WHERE type_feature::text = 'checkbox';"
        self.cur.execute(query)
        self.feature_id_checkbox = [feature_id[0] for feature_id in self.cur]

    def download_feature_id_name_select(self) -> None:
        """
        Загрузка словаря соответствия feature_id и названия
        для харакетристик с типом select
        """
        query = "SELECT feature_id, name FROM feature " \
                "WHERE type_feature::text = 'select';"
        self.cur.execute(query)

        self.feature_id_name_select = {feature[0]: feature[1]
                                       for feature in self.cur}


class DownloadCategoryDirector():
    """Класс директор для загрузки данных из БД"""

    def __init__(self, builder: DownloadDataBuilder) -> None:
        self._builder = builder

    def get_category_data_obj(self) -> CategoryData:
        """Загрузка данных и создание класса CategoryData"""
        self._builder.download_category_ids()
        self._builder.download_category_feature()
        self._builder.download_feature_id_checkbox()
        self._builder.download_feature_id_name_select()
        return CategoryData(
            category_ids=self._builder.category_ids,
            category_feature=self._builder.category_feature,
            feature_id_checkbox=self._builder.feature_id_checkbox,
            feature_id_name_select=self._builder.feature_id_name_select
        )


class LoadDataBuilder(Builder):
    """Класс строитель для загрузки фэйковых данных в БД"""
    def __init__(self, cur: cursor, category_data_obj: CategoryData,) -> None:
        self.cur = cur
        self.category_data_obj = category_data_obj
        self.manufacturer_ids = [
            str(uuid.uuid4()) for _ in range(MANUFACTURERS_COUNT)
        ]
        self.product_category = {}
        self.data_images = []

    def load_manufacturer(self):
        query = 'INSERT INTO manufacturer (id, manufacturer_id, ' \
                'name, description, updated) VALUES (%s, %s, %s, %s, %s)'
        data_manufacturers = [(fake.uuid4(), uk, fake.company(),
                               fake.sentence(nb_words=10), now)
                              for uk in self.manufacturer_ids]

        execute_batch(self.cur, query, data_manufacturers)

    def load_product(self):
        query = 'INSERT INTO product (id, product_id, name, slug, ' \
                'description, price, main_image, added, updated, count, ' \
                'is_limited, category_fk, manufacturer_fk) ' \
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        data_products = []
        counter = 0

        for num, category_id in enumerate(self.category_data_obj.category_ids):
            product_ids = [str(uuid.uuid4())
                           for _ in range(PRODUCTS_IN_CATEGORY_COUNT)]

            for product_num, product_id in enumerate(product_ids):
                self.product_category.update({product_id: category_id})

                is_limited = True if product_num <= PRODUCTS_LIMITED_COUNT \
                    else False

                counter += 1

                data_products.append(
                    (fake.uuid4(), product_id, fake.company(),
                     f'product-{counter}', fake.sentence(nb_words=20),
                     round(random.uniform(100, 10_000), 2), IMAGE_LINKS[num],
                     fake.date_time(), now, random.randint(0, 50),
                     is_limited, category_id,
                     random.choice(self.manufacturer_ids))
                )

                self.data_images.extend([
                    (fake.uuid4(), fake.uuid4(), IMAGE_LINKS[num], product_id)
                    for _ in range(random.randint(1, 4))
                ])

        execute_batch(self.cur, query, data_products, page_size=PAGE_SIZE)

    def load_image(self):
        query = 'INSERT INTO image (id, image_id, image, product_fk) ' \
                'VALUES (%s, %s, %s, %s)'

        execute_batch(self.cur, query, self.data_images, page_size=PAGE_SIZE)

    def load_product_feature(self):
        query = 'INSERT INTO product_feature ' \
                '(id, product_fk, feature_fk, value) ' \
                'VALUES (%s, %s, %s, %s)'

        data_product_feature = []

        for product_id in self.product_category.keys():
            category_id = self.product_category.get(product_id)
            feature_list = \
                self.category_data_obj.category_feature.get(category_id)
            for feature_id in feature_list:
                if feature_id in self.category_data_obj.feature_id_checkbox:
                    data_product_feature.append(
                        (str(uuid.uuid4()), product_id, feature_id,
                         random.choice(['yes', 'no'])))
                elif feature_id in self.category_data_obj\
                        .feature_id_name_select.keys():
                    data_product_feature.append(
                        (str(uuid.uuid4()), product_id, feature_id,
                         random.choice(
                             FEATURES_VALUE.get(
                                 self.category_data_obj
                                 .feature_id_name_select[feature_id])
                         )))
                elif feature_id in FEATURES_GROUP_TEXT.keys():
                    data_product_feature.append((
                        str(uuid.uuid4()),
                        product_id,
                        feature_id,
                        ', '.join(set(random.choices(
                            FEATURES_GROUP_TEXT.get(feature_id), k=3)
                        ))))
                else:
                    data_product_feature.append(
                        (str(uuid.uuid4()), product_id, feature_id,
                         fake.word()))

        execute_batch(self.cur, query, data_product_feature,
                      page_size=PAGE_SIZE)


class LoadDataDirector():
    """Класс директор для загрузки фейковых данный в БД"""
    def __init__(self, builder: LoadDataBuilder) -> None:
        self._builder = builder

    def load_fake_data(self) -> None:
        """Загрузка данных и создание класса CategoryData"""
        self._builder.load_manufacturer()
        self._builder.load_product()
        self._builder.load_image()
        self._builder.load_product_feature()


class CategoryDataHandler():
    """Обработчик процесса получения данных и формирования объекта.
    Внешний интерфейс"""
    def __init__(self, cur: cursor) -> None:
        builder = DownloadDataBuilder(cur)
        self.director = DownloadCategoryDirector(builder)

    def __call__(self) -> CategoryData:
        category_data_handler = self.director.get_category_data_obj()
        return category_data_handler


class ProductLoadDataHandler():
    """Обработчик процесса заполнения БД фейковыми данными
    Внешний интерфейс"""
    def __init__(self, cur: cursor, category_data_obj: CategoryData):
        builder = LoadDataBuilder(cur, category_data_obj)
        self.direct = LoadDataDirector(builder)

    def __call__(self) -> None:
        self.direct.load_fake_data()


if __name__ == '__main__':
    fake = Faker()
    now = datetime.utcnow()

    with psycopg2.connect(**DSN) as conn, conn.cursor() as curs:
        download_handler = CategoryDataHandler(curs)
        category_data = download_handler()

        load_handler = ProductLoadDataHandler(curs, category_data)
        load_handler()

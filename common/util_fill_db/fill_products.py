import random
import uuid
from abc import ABC
from dataclasses import dataclass, astuple

from datetime import datetime
from typing import List, Dict

import psycopg2
from faker import Faker
from psycopg2.extras import execute_batch
from psycopg2.extensions import cursor

from common.util_fill_db.settings import MANUFACTURERS_COUNT, PAGE_SIZE, \
    PRODUCTS_IN_CATEGORY_COUNT, IMAGE_LINKS, \
    FEATURES_VALUE, FEATURES_GROUP_TEXT, DSN


@dataclass
class CategoryData():
    """Объект с загруженными данными из БД"""
    category_ids: List[str]
    category_feature: Dict[str, List[str]]
    feature_id_checkbox: List[str]
    feature_id_name_select: Dict[str, str]


@dataclass
class Manufacturer():
    id: str
    manufacturer_id: str
    name: str
    description: str
    updated: datetime


@dataclass
class Product():
    id: str
    product_id: str
    name: str
    slug: str
    description: str
    price: float
    main_image: str
    added: datetime
    updated: datetime
    count: int
    is_limited: bool
    category_fk: str
    manufacturer_fk: str


@dataclass
class Image():
    id: str
    image_id: str
    image: str
    product_id: str


@dataclass
class ProductFeature():
    id: str
    product_fk: str
    feature_fk: str
    value: str


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
        для характеристик с типом select
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
    """
    Класс строитель для загрузки фэйковых данных в БД
    Args:
        cur: курсор подключения к postgres
        category_data_obj: объект с данными из postgres
    """
    def __init__(self, cur: cursor, category_data_obj: CategoryData) -> None:
        self.cur = cur
        self.category_data_obj = category_data_obj
        self.manufacturers = [
            Manufacturer(id=str(uuid.uuid4()),
                         manufacturer_id=str(uuid.uuid4()),
                         name=fake.company(),
                         description=fake.sentence(nb_words=10),
                         updated=now)
            for _ in range(MANUFACTURERS_COUNT)
        ]
        self.products, self.images, self.product_feature = [], [], []

    def load_manufacturer(self) -> None:
        """Загрузка фэйковых производителей"""
        query = 'INSERT INTO manufacturer (id, manufacturer_id, ' \
                'name, description, updated) VALUES (%s, %s, %s, %s, %s)'
        data_manufacturers = [astuple(manufacturer)
                              for manufacturer in self.manufacturers]
        execute_batch(self.cur, query, data_manufacturers)

    def load_product(self) -> None:
        """Загрузка фэйковых товаров"""
        query = 'INSERT INTO product (id, product_id, name, slug, ' \
                'description, price, main_image, added, updated, count, ' \
                'is_limited, category_fk, manufacturer_fk) ' \
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        for num, category_id in enumerate(self.category_data_obj.category_ids):
            products_current = [
                Product(id=str(uuid.uuid4()), product_id=str(uuid.uuid4()),
                        name=fake.company(),
                        slug=f'product-{num}-{product_num}',
                        description=fake.sentence(nb_words=20),
                        price=round(random.uniform(100, 10_000), 2),
                        main_image=IMAGE_LINKS[num],
                        added=now, updated=now, count=random.randint(0, 50),
                        is_limited=random.choice([True, False]),
                        category_fk=category_id,
                        manufacturer_fk=random.choice(self.manufacturers)
                        .manufacturer_id)
                for product_num in range(PRODUCTS_IN_CATEGORY_COUNT)
            ]

            images_current = [
                Image(id=str(uuid.uuid4()), image_id=str(uuid.uuid4()),
                      image=IMAGE_LINKS[num], product_id=product.product_id)
                for _ in range(random.randint(1, 4))
                for product in products_current
            ]

            self.products.extend(products_current)
            self.images.extend(images_current)

        data_products = [astuple(product) for product in self.products]
        execute_batch(self.cur, query, data_products, page_size=PAGE_SIZE)

    def load_image(self) -> None:
        """Загрузка изображений к товарам"""
        query = 'INSERT INTO image (id, image_id, image, product_fk) ' \
                'VALUES (%s, %s, %s, %s)'
        data_images = [astuple(image) for image in self.images]
        execute_batch(self.cur, query, data_images, page_size=PAGE_SIZE)

    def _get_value_feature(self, feature_id: str) -> str:
        """
        Возвращает значение характеристики в зависимости от типа
        :param feature_id: feature_id характеристики из БД
        :return: value
        """
        if feature_id in self.category_data_obj.feature_id_checkbox:
            value_cur = random.choice(['yes', 'no'])
        elif feature_id in self.category_data_obj \
                .feature_id_name_select.keys():
            value_cur = random.choice(
                FEATURES_VALUE.get(self.category_data_obj
                                   .feature_id_name_select[
                                       feature_id]))
        elif feature_id in FEATURES_GROUP_TEXT.keys():
            value_cur = ', '.join(set(random.choices(
                FEATURES_GROUP_TEXT.get(feature_id), k=3)
            ))
        else:
            value_cur = fake.word()
        return value_cur

    def load_product_feature(self) -> None:
        """Загрузка связи many-to-many товаров и характеристик к ним"""
        query = 'INSERT INTO product_feature ' \
                '(id, product_fk, feature_fk, value) ' \
                'VALUES (%s, %s, %s, %s)'

        for product in self.products:
            category_id = product.category_fk

            feature_list = \
                self.category_data_obj.category_feature.get(category_id)

            self.product_feature.extend(
                [ProductFeature(id=str(uuid.uuid4()),
                                product_fk=product.product_id,
                                feature_fk=feature_id,
                                value=self._get_value_feature(feature_id))
                 for feature_id in feature_list]
            )

        data_product_feature = [astuple(product_feature)
                                for product_feature in self.product_feature]
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
    now = datetime.now()

    with psycopg2.connect(**DSN) as conn, conn.cursor() as curs:
        download_handler = CategoryDataHandler(curs)
        category_data = download_handler()

        load_handler = ProductLoadDataHandler(curs, category_data)
        load_handler()

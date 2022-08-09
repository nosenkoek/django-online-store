from uuid import uuid4

from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_products.models import Product, Manufacturer
from app_categories.models import Category

PRODUCT = {
    'id': str(uuid4()),
    'product_id': str(uuid4()),
    'name': 'product_1',
    'description': 'text',
    'price': 10_000,
    'is_limited': True,
}

MANUFACTURER = {
    'id': str(uuid4()),
    'manufacturer_id': str(uuid4()),
    'name': 'manufacturer'
}

CATEGORY = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'category_name',
    'icon': None,
    'is_active': True,
    'parent_id': None,
}


class BaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        category = Category.objects.create(**CATEGORY)
        manufacturer = Manufacturer.objects.create(**MANUFACTURER)
        Product.objects.create(**PRODUCT, category_fk=category, manufacturer_fk=manufacturer)


class TestProduct(BaseModelTest):
    product = Product.objects.first()

    def test_name_label(self) -> None:
        """Проверка подписи поля названия товара"""
        field_label = self.product._meta.get_field('name').verbose_name
        self.assertEquals(field_label,  _('name'))

    def test_description_label(self) -> None:
        """Проверка подписи поля описания товара"""
        field_label = self.product._meta.get_field('description').verbose_name
        self.assertEquals(field_label,  _('description'))

    def test_price_label(self) -> None:
        """Проверка подписи поля цены товара"""
        field_label = self.product._meta.get_field('price').verbose_name
        self.assertEquals(field_label,  _('price'))

    def test_is_limited_label(self) -> None:
        """Проверка подписи поля лимитирован ли товар"""
        field_label = self.product._meta.get_field('is_limited').verbose_name
        self.assertEquals(field_label,  _('is limited'))

    def test_category_label(self) -> None:
        """Проверка подписи поля категории товара"""
        field_label = self.product._meta.get_field('category_fk').verbose_name
        self.assertEquals(field_label,  _('category'))

    def test_manufacturer_label(self) -> None:
        """Проверка подписи поля категории товара"""
        field_label = self.product._meta.get_field('manufacturer_fk').verbose_name
        self.assertEquals(field_label,  _('manufacturer'))

from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_products.models import Product, Manufacturer
from app_categories.models import Category

from app_products.tests.settings import CATEGORY_PARENT, CATEGORY, \
    MANUFACTURER, PRODUCT


class BaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        Category.objects.create(**CATEGORY_PARENT)
        category = Category.objects.create(**CATEGORY)
        manufacturer = Manufacturer.objects.create(**MANUFACTURER)
        cls.product = Product.objects.create(**PRODUCT,
                                             category_fk=category,
                                             manufacturer_fk=manufacturer)


class TestProduct(BaseModelTest):
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

    def test_count_label(self) -> None:
        """Проверка подписи поля количества товара"""
        field_label = self.product._meta.get_field('count').verbose_name
        self.assertEquals(field_label,  _('count_in_storage'))

    def test_category_label(self) -> None:
        """Проверка подписи поля категории товара"""
        field_label = self.product._meta.get_field('category_fk').verbose_name
        self.assertEquals(field_label,  _('category'))

    def test_manufacturer_label(self) -> None:
        """Проверка подписи поля категории товара"""
        field_label = self.product._meta\
            .get_field('manufacturer_fk')\
            .verbose_name
        self.assertEquals(field_label,  _('manufacturer'))

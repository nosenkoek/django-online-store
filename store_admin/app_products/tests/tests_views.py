import os
import shutil
from math import ceil
from random import randint
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.conf import settings
from django.db import connection
from django.urls import reverse
from django.shortcuts import resolve_url

from app_categories.models import Category, Feature, CategoryFeature
from app_products.models import Manufacturer, Product
from app_products.tests.settings import CATEGORY_PARENT, CATEGORY, \
    FEATURE_LIST, MANUFACTURER, COUNT_PRODUCT_IN_PAGE

TEMP_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'temp_media/')

NUMBERS_PRODUCT = 20


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTest(TestCase):
    @classmethod
    @property
    def gif_1(cls):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        gif_1 = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        return gif_1

    @classmethod
    def setUpTestData(cls):
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        Category.objects.create(**CATEGORY_PARENT)
        subcategory = Category.objects.create(**CATEGORY)

        features = [Feature(**feature) for feature in FEATURE_LIST]
        Feature.objects.bulk_create(features)

        feature_category = [
            CategoryFeature(category_fk=subcategory, feature_fk=feature)
            for feature in features]
        CategoryFeature.objects.bulk_create(feature_category)

        manufacturer = Manufacturer.objects.create(**MANUFACTURER)

        products = [
            Product(id=str(uuid4()), product_id=str(uuid4()),
                    name=f'name_{num}', is_limited=True, count=10,
                    slug=f'product-{num}', description='text',
                    price=randint(0, 100), image=cls.gif_1,
                    category_fk=subcategory, manufacturer_fk=manufacturer)
            for num in range(NUMBERS_PRODUCT)
        ]
        Product.objects.bulk_create(products)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


class ProductListTest(BaseTest):
    def setUp(self) -> None:
        self.category = Category.objects.get(parent=None)
        self.subcategory = Category.objects.get(parent=self.category)

    def test_products_list_url(self):
        """Проверка открытия со списком товаров"""
        response = self.client.get(
            f'/{self.category.slug}/{self.subcategory.slug}'
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            f'/{self.category.slug}/{self.subcategory.slug}',
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_products_list_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(
            f'/{self.category.slug}/{self.subcategory.slug}',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'app_products/list_products.html')

    def test_categories_number(self):
        """Проверка количества отображаемых категорий в навигации"""
        response = self.client.get(
            f'/{self.category.slug}/{self.subcategory.slug}',
            follow=True
        )
        self.assertEqual(1, len(response.context.get('navi_categories')))

    def test_products_number(self):
        """Проверка количества отображаемых товаров"""
        page_count = ceil(NUMBERS_PRODUCT / COUNT_PRODUCT_IN_PAGE)
        products = 0

        for page_num in range(1, page_count + 1):
            response = self.client.get(
                f'/{self.category.slug}/{self.subcategory.slug}',
                {'page': page_num},
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            products += len(response.context.get('products'))

        self.assertTrue(products == NUMBERS_PRODUCT)

    def test_sorting_price(self):
        """Проверка сортировки по цене"""
        #TODO: доделать
        page_count = ceil(NUMBERS_PRODUCT / COUNT_PRODUCT_IN_PAGE)
        price_current = 0

        for page_num in range(1, page_count + 1):
            response = self.client.get(
                f'/{self.category.slug}/{self.subcategory.slug}/?sort=price',
                {'page': page_num},
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            products = response.context.get('products')
            for product in products:
                print(product.name, product.price)
            price_first = products.all().first().price
            price_last = products.all().last().price
            print(price_first, price_last)
            self.assertTrue(price_first <= price_last)
            self.assertTrue(price_current <= price_last)
            price_current = price_last

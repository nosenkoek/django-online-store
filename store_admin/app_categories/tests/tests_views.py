import os
import shutil
from time import sleep
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.db import connection
from django.urls import reverse
from django.conf import settings

from app_categories.models import Category
from app_products.models import Product, Manufacturer
from app_products.services.decorator_count_views import SECONDS_CACHE, \
    NAME_ATRS_CACHE
from utils.context_managers import redis_connection

TEMP_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'temp_media/')

NUMBERS_PRODUCT_TO_DB = 20

NUMBERS_CATEGORY = 10
NUMBERS_RANDOM_CATEGORY = 3
NUMBERS_POPULAR_PRODUCTS = 8
NUMBERS_LIMIT_PRODUCTS = 16


class PullDatabaseMixin():
    @classmethod
    def insert_category(cls):
        categories = [
            Category(id=str(uuid4()), category_id=str(uuid4()),
                     name=f'name_{num}', slug=f'name-{num}', is_active=True)
            for num in range(NUMBERS_CATEGORY)
        ]

        categories[-1].is_active = False

        Category.objects.bulk_create(categories)
        Category.objects.rebuild()

        cls.subcategories = [
            Category(id=str(uuid4()), category_id=str(uuid4()),
                     name=f'subname_{num}', slug=f'subname-{num}',
                     is_active=True, parent=categories[0], image=cls.gif_1)
            for num in range(NUMBERS_CATEGORY)
        ]

        Category.objects.bulk_create(cls.subcategories)
        Category.objects.rebuild()

    @classmethod
    @property
    def manufacturer(cls):
        return Manufacturer.objects.create(name='manufacturer')

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
    def insert_products(cls):
        products = [
            Product(id=str(uuid4()), product_id=str(uuid4()),
                    name=f'name_{num}', is_limited=True, count=10,
                    slug=f'product-{num}', description='text',
                    price=1_000, main_image=cls.gif_1,
                    category_fk=cls.subcategories[0],
                    manufacturer_fk=cls.manufacturer)
            for num in range(NUMBERS_PRODUCT_TO_DB)
        ]
        Product.objects.bulk_create(products)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTest(TestCase, PullDatabaseMixin):
    @classmethod
    def setUpTestData(cls):
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        cls.insert_category()
        cls.insert_products()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        with redis_connection() as redis_conn:
            redis_conn.delete(*NAME_ATRS_CACHE.get('testserver'))


class MainPageTest(BaseTest):
    def test_main_page_url(self):
        """Проверка открытия главной страницы(с переходом на выбранный язык)"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_main_page_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(reverse('main_page'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_categories/main_page.html')

    def test_categories_number(self):
        """Проверка количества отображаемых категорий в навигации"""
        response = self.client.get('/', follow=True)
        self.assertEqual(NUMBERS_CATEGORY - 1,
                         len(response.context.get('navi_categories')))

    def test_random_categories_number(self):
        """Проверка количества отображаемых категорий"""
        response = self.client.get('/', follow=True)
        self.assertEqual(NUMBERS_RANDOM_CATEGORY,
                         len(response.context.get('random_categories')))

    def test_popular_products_number(self):
        """Проверка количества отображаемых популярных товаров"""
        products = Product.objects.order_by('?')[:NUMBERS_POPULAR_PRODUCTS]

        for product in products:
            self.client.get(f'/catalog/{product.slug}', follow=True)
            sleep(SECONDS_CACHE / NUMBERS_POPULAR_PRODUCTS)

        response = self.client.get('/', follow=True)
        self.assertEqual(NUMBERS_POPULAR_PRODUCTS,
                         len(response.context.get('popular_products')))

    def test_limit_products_number(self):
        """Проверка количества отображаемых лимитированных товаров"""
        response = self.client.get('/', follow=True)
        self.assertEqual(NUMBERS_LIMIT_PRODUCTS,
                         len(response.context.get('limit_edition')))


class SubcategoriesListTest(BaseTest):
    def setUp(self) -> None:
        self.category = Category.objects.filter(parent=None).first()

    def test_subcategories_url(self):
        """Проверка открытия со списком подкатегорий"""
        response = self.client.get(f'/{self.category.slug}')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(f'/{self.category.slug}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_subcategories_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(
            reverse('subcategory_list', args=[self.category.slug]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'app_categories/subcategory_list.html')

    def test_categories_number(self):
        """Проверка количества отображаемых категорий в навигации"""
        response = self.client.get(
            reverse('subcategory_list', args=[self.category.slug]),
            follow=True
        )
        self.assertEqual(NUMBERS_CATEGORY - 1,
                         len(response.context.get('navi_categories')))

    def test_subcategories_number(self):
        """Проверка количества отображаемых лимитированных товаров"""
        response = self.client.get(
            reverse('subcategory_list', args=[self.category.slug]),
            follow=True
        )
        self.assertEqual(NUMBERS_CATEGORY,
                         len(response.context.get('subcategories')))

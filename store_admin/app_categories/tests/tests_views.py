import shutil
from time import sleep

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.db import connection
from django.urls import reverse

from app_categories.models import Category
from app_products.models import Product
from app_products.services.decorator_count_views import SECONDS_CACHE, \
    NAME_ATRS_CACHE
from utils.context_managers import redis_connection
from app_categories.tests.settings import TEMP_MEDIA_ROOT, NUMBERS_CATEGORY, \
    NUMBERS_RANDOM_CATEGORY, NUMBERS_POPULAR_PRODUCTS, NUMBERS_LIMIT_PRODUCTS


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTest(TestCase):
    fixtures = ['app_categories/tests/fixtures/fixtures_test_category.json']

    @classmethod
    def setUpClass(cls):
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        SimpleUploadedFile(name='small_1.gif',
                           content=(b'\x47\x49\x46\x38\x39\x61\x02\x00'
                                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                                    b'\x0A\x00\x3B'),
                           content_type='image/gif')
        super(BaseTest, cls).setUpClass()

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
        self.assertEqual(NUMBERS_CATEGORY,
                         len(response.context.get('navi_categories')))

    def test_random_categories_number(self):
        """Проверка количества отображаемых категорий"""
        response = self.client.get('/', follow=True)
        self.assertEqual(NUMBERS_RANDOM_CATEGORY,
                         len(response.context.get('random_categories')))

    def test_popular_products_number(self):
        """Проверка количества отображаемых популярных товаров"""
        products = Product.objects \
            .order_by('-added')[:NUMBERS_POPULAR_PRODUCTS]

        for product in products:
            self.client.get(f'/catalog/{product.slug}', follow=True)
            sleep(SECONDS_CACHE / NUMBERS_POPULAR_PRODUCTS)

        response = self.client.get('/', follow=True)
        self.assertTrue(
            len(response.context.get('popular_products')) in
            [NUMBERS_POPULAR_PRODUCTS - 1, NUMBERS_POPULAR_PRODUCTS,
             NUMBERS_POPULAR_PRODUCTS + 1]
        )

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
        self.assertEqual(NUMBERS_CATEGORY,
                         len(response.context.get('navi_categories')))

    def test_subcategories_number(self):
        """Проверка количества отображаемых подкатегорий"""
        response = self.client.get(
            reverse('subcategory_list', args=[self.category.slug]),
            follow=True
        )
        self.assertEqual(NUMBERS_CATEGORY,
                         len(response.context.get('subcategories')))

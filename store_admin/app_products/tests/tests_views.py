import shutil
from math import ceil
from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.db import connection
from django.urls import reverse

from app_categories.models import Category
from app_products.models import Product, Feedback
from app_products.services.decorator_count_views import NAME_ATRS_CACHE
from app_products.tests.settings import COUNT_PRODUCT_IN_PAGE, \
    TEMP_MEDIA_ROOT, PRICE_FROM, PRICE_TO, NUMBERS_PRODUCT, USERNAME, PASSWORD
from utils.context_managers import redis_connection


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTest(TestCase):
    fixtures = ['app_products/tests/fixtures/fixtures_test_product_view.json']

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


class ProductListTest(BaseTest):
    def setUp(self) -> None:
        self.category = Category.objects.get(parent=None)
        self.subcategory = Category.objects.get(parent=self.category)
        self.page_count = ceil(NUMBERS_PRODUCT / COUNT_PRODUCT_IN_PAGE)
        self.main_url = \
            f'/catalog/{self.category.slug}/{self.subcategory.slug}'

    def test_products_list_url(self):
        """Проверка открытия со списком товаров"""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_products_list_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'app_products/product_list.html')

    def test_products_number(self):
        """Проверка количества отображаемых товаров"""
        products = 0

        for page_num in range(1, self.page_count + 1):
            response = self.client.get(self.main_url,
                                       {'page': page_num},
                                       follow=True)
            self.assertEqual(response.status_code, 200)
            products += len(response.context.get('products'))

        self.assertTrue(products == NUMBERS_PRODUCT)

    def test_sorting_price(self):
        """Проверка сортировки по цене"""
        price_current = 0

        for page_num in range(1, self.page_count + 1):
            response = self.client.get(
                f'{self.main_url}/?page={page_num}&sort=price',
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            products = response.context.get('products')
            price_first = products[:1][0].price
            price_last = products[(len(products) - 1):][0].price

            self.assertTrue(price_first <= price_last)
            self.assertTrue(price_current <= price_last)
            price_current = price_last

    def test_sorting_added(self):
        """Проверка сортировки по новизне"""
        added_current = datetime(1970, 1, 1, 0, 0, 0)

        for page_num in range(1, self.page_count + 1):
            response = self.client.get(
                f'{self.main_url}/?page={page_num}&sort=added',
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            products = response.context.get('products')
            added_first = products[:1][0].added
            added_last = products[(len(products) - 1):][0].added

            self.assertTrue(added_first <= added_last)
            self.assertTrue(added_current <= added_last)
            added_current = added_last

    def test_filter_price(self):
        """Проверка фильтрации по стоимости"""
        response = self.client.get(
            f'{self.main_url}/?price={PRICE_FROM};{PRICE_TO}&sort=price',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        products = response.context.get('products')
        price_first = products.all().first().price
        self.assertTrue(PRICE_FROM <= price_first)

        response = self.client.get(
            f'{self.main_url}/?price={PRICE_FROM};{PRICE_TO}&sort=-price',
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        products = response.context.get('products')
        price_first = products.all().first().price
        self.assertTrue(price_first <= PRICE_TO)


class ProductDetailTest(BaseTest):
    def setUp(self) -> None:
        self.product = Product.objects.last()
        self.main_url = f'/catalog/{self.product.slug}'
        user = User.objects.create(username=USERNAME)
        user.set_password(PASSWORD)
        user.save()
        self.feedback = Feedback.objects.create(text='test text',
                                                user_fk=user,
                                                product_fk=self.product)

    def test_product_url(self):
        """Проверка открытия детальной страницы товара"""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_products_list_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'app_products/product_detail.html')

    def test_feedback_show(self):
        """Проверка отображения отзывов"""
        response = self.client.get(self.main_url, follow=True)
        queryset_feedback = Feedback.objects.filter(product_fk=self.product)
        self.assertQuerysetEqual(response.context.get('feedbacks'),
                                 queryset_feedback)

    def test_new_feedback(self):
        """Проверка добавления отзыва"""
        pass


class PopularProductTest(BaseTest):
    def setUp(self) -> None:
        self.main_url = '/catalog/popular_product'

    def test_popular_product_url(self):
        """Проверка открытия страницы популярных товаров"""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('popular_product_list'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_popular_products_list_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(reverse('popular_product_list'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'app_products/popular_product_list.html')

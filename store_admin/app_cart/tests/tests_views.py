from django.test import TestCase
from django.db import connection
from django.urls import reverse

from app_products.models import Product


class AddProductToCartMixin():
    def add_product_to_cart(self) -> None:
        """Добавление товара 1 в корзину"""
        self.client.get(f'/cart/product_add/{self.product.product_id}',
                        data={'next': '/'},
                        follow=True)


class CheckCartEmptyMixin():
    def check_cart_is_empty(self) -> None:
        """Проверка, что корзина пуста"""
        response = self.client.get('/cart/view', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('cart')), 0)


class BaseTest(TestCase):
    fixtures = ['app_cart/tests/fixtures/fixtures_test_cart.json']

    @classmethod
    def setUpClass(cls):
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        super(BaseTest, cls).setUpClass()

        cls.product = Product.objects.first()


class CartTest(BaseTest):
    def setUp(self) -> None:
        self.main_url = '/cart/view'

    def test_cart_url(self):
        """Проверка открытия страницы корзины"""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_cart_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_cart/cart.html')


class AddProductCart(BaseTest):
    def test_add_product_to_cart(self):
        """Проверка добавления 1 товара"""
        response = self.client.get(f'/cart/product_add/'
                                   f'{self.product.product_id}',
                                   data={'next': '/'},
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/cart/view', follow=True)
        self.assertEqual(len(response.context.get('cart')), 1)


class RemoveProductCart(BaseTest, AddProductToCartMixin, CheckCartEmptyMixin):
    def test_remove_product_from_cart(self):
        """Проверка удаления 1 товара"""
        self.add_product_to_cart()
        response = self.client.get(f'/cart/product_remove/'
                                   f'{self.product.product_id}',
                                   data={'next': '/'},
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.check_cart_is_empty()


class DeleteAllProductCart(BaseTest, AddProductToCartMixin,
                           CheckCartEmptyMixin):
    def test_delete__all_products_from_cart(self):
        """Проверка удаления всех товаров 1 типа"""
        self.add_product_to_cart()
        response = self.client.get(f'/cart/product_delete/'
                                   f'{self.product.product_id}',
                                   data={'next': '/'},
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.check_cart_is_empty()


class UpdateProductCart(BaseTest, AddProductToCartMixin):
    def test_update_count_products(self):
        """Проверка изменения количества в корзине"""
        self.add_product_to_cart()
        url = reverse('cart_update_product',
                      kwargs={'product_id': self.product.product_id})
        response = self.client.post(
            f'{url}?next=/',
            data={'quantity': 2, 'update': 1},
            follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('cart'), follow=True)
        self.assertEqual(
            response.context.get('cart').get_quantity(self.product.product_id),
            2
        )


class ClearCart(BaseTest, AddProductToCartMixin, CheckCartEmptyMixin):
    def test_clear_cart(self):
        """Проверка очистки корзины"""
        for _ in range(3):
            self.add_product_to_cart()
        response = self.client.get(reverse('cart_clear'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.check_cart_is_empty()

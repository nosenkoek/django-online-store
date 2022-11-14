from django.test import TestCase
from django.urls import reverse
from django.db import connection

from app_order.models import Order


class BaseTest(TestCase):
    fixtures = \
        ['app_order/tests/fixtures/fixtures_test_order_view.json']

    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        super(BaseTest, cls).setUpClass()

    def _login_user(self):
        self.client.login(username='user', password='test12345')


class OrderHistoryTest(BaseTest):
    def test_order_history_page_url(self):
        """Проверка открытия страницы истории заказов"""
        self._login_user()
        response = self.client.get('/order/history/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_order_history_template(self):
        """Проверка используемого шаблона"""
        self._login_user()
        response = self.client.get(reverse('order_history'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_order/order_history.html')

    def test_orders_number(self):
        """Проверка количества отображаемых заказов"""
        self._login_user()
        response = self.client.get(reverse('order_history'), follow=True)
        self.assertEqual(1, len(response.context.get('orders')))


class OrderDetailTest(BaseTest):
    def setUp(self) -> None:
        self.order = Order.objects.first()

    def test_order_page_url(self):
        """Проверка открытия страницы детальной информации о заказе"""
        self._login_user()
        response = self.client.get(f'/order/{self.order.number}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_order_template(self):
        """Проверка используемого шаблона"""
        self._login_user()
        response = self.client.get(f'/order/{self.order.number}', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_order/order_detail.html')


class CheckoutTest(BaseTest):
    def test_checkout_page_url(self):
        """Проверка открытия страницы создания заказа"""
        self._login_user()
        response = self.client.get('/order/checkout', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_checkout_template(self):
        """Проверка используемого шаблона"""
        self._login_user()
        response = self.client.get(reverse('order'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_order/checkout.html')

    # todo: придумать тестирование создание заказа

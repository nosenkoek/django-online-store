from django.test import TestCase
from django.urls import reverse
from django.db import connection

from app_order.models import Order


class BaseTest(TestCase):
    fixtures = \
        ['app_payment/tests/fixtures/fixtures_test_payment_view.json']

    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        super(BaseTest, cls).setUpClass()

    def setUp(self) -> None:
        self._order = Order.objects.first()
        self._order_id = self._order.order_id


class PaymentTest(BaseTest):
    def test_payment_page_url(self):
        """Проверка открытия страницы оплаты"""
        response = self.client.get(f'/payment/pay/{self._order_id}',
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_payment_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(reverse('pay', args=(self._order_id,)),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_payment/payment_form.html')

    def test_pay_order(self):
        """Проверка оплаты заказа"""
        data = {'number': '1235 5488'}
        response = self.client.post(reverse('pay', args=(self._order_id,)),
                                    data=data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_payment/payment_progress.html')


class PaymentProgressTest(BaseTest):
    def test_payment_progress_page_url(self):
        """Проверка открытия страницы оплаты"""
        response = self.client.get(f'/payment/progress/{self._order_id}',
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_payment_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(reverse('payment_progress',
                                           args=(self._order_id,)),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_payment/payment_progress.html')

from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_order.models import Payment


class TestPayment(TestCase):
    fixtures = \
        ['app_payment/tests/fixtures/fixtures_test_payment_model.json']

    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())
        super(TestPayment, cls).setUpClass()

    def setUp(self) -> None:
        self.payment = Payment.objects.first()

    def test_paid_label(self) -> None:
        """Проверка подписи поля даты оплаты"""
        field_label = self.payment._meta.get_field('paid').verbose_name
        self.assertEquals(field_label,  _('date of paid'))

    def test_error_label(self) -> None:
        """Проверка подписи поля ошибки оплаты"""
        field_label = self.payment._meta.get_field('error').verbose_name
        self.assertEquals(field_label,  _('error'))

    def test_payment_method_label(self) -> None:
        """Проверка подписи поля метода оплаты"""
        field_label = self.payment._meta.get_field('payment_method')\
            .verbose_name
        self.assertEquals(field_label,  _('payment method'))

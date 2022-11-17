from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_order.models import DeliveryMethod, Delivery, Order


class BaseModelTest(TestCase):
    fixtures = \
        ['app_order/tests/fixtures/fixtures_test_order_model.json']

    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        super(BaseModelTest, cls).setUpClass()


class TestDeliveryMethod(BaseModelTest):
    def setUp(self) -> None:
        self.delivery_method = DeliveryMethod.objects.first()

    def test_name_label(self) -> None:
        """Проверка подписи поля названия метода доставки"""
        field_label = self.delivery_method._meta.get_field('name').verbose_name
        self.assertEquals(field_label,  _('name'))

    def test_price_label(self) -> None:
        """Проверка подписи поля цены доставки"""
        field_label = self.delivery_method._meta.get_field('price')\
            .verbose_name
        self.assertEquals(field_label,  _('price'))

    def test_free_from_label(self) -> None:
        """Проверка подписи поля бесплатная доставка от """
        field_label = self.delivery_method._meta.get_field('free_from')\
            .verbose_name
        self.assertEquals(field_label,  _('price_free_from'))


class TestDelivery(BaseModelTest):
    def setUp(self) -> None:
        self.delivery = Delivery.objects.first()

    def test_city_label(self) -> None:
        """Проверка подписи поля города доставки"""
        field_label = self.delivery._meta.get_field('city').verbose_name
        self.assertEquals(field_label,  _('city'))

    def test_address_label(self) -> None:
        """Проверка подписи поля адреса доставки"""
        field_label = self.delivery._meta.get_field('address').verbose_name
        self.assertEquals(field_label,  _('address'))

    def test_delivery_method_label(self) -> None:
        """Проверка подписи поля способа доставки"""
        field_label = self.delivery._meta.get_field('delivery_method_fk')\
            .verbose_name
        self.assertEquals(field_label,  _('delivery method'))


class TestOrder(BaseModelTest):
    def setUp(self) -> None:
        self.order = Order.objects.first()

    def test_created_label(self) -> None:
        """Проверка подписи поля даты создания заказа"""
        field_label = self.order._meta.get_field('created').verbose_name
        self.assertEquals(field_label,  _('created'))

    def test_number_label(self) -> None:
        """Проверка подписи поля номера заказа"""
        field_label = self.order._meta.get_field('number').verbose_name
        self.assertEquals(field_label,  _('number'))

    def test_total_price_label(self) -> None:
        """Проверка подписи поля полной стоимости заказа"""
        field_label = self.order._meta.get_field('total_price').verbose_name
        self.assertEquals(field_label,  _('total price'))

    def test_status_label(self) -> None:
        """Проверка подписи поля статуса заказа"""
        field_label = self.order._meta.get_field('status').verbose_name
        self.assertEquals(field_label,  _('status'))

    def test_delivery_fk_label(self) -> None:
        """Проверка подписи поля доставки"""
        field_label = self.order._meta.get_field('delivery_fk').verbose_name
        self.assertEquals(field_label,  _('delivery'))

    def test_payment_fk_label(self) -> None:
        """Проверка подписи поля оплаты"""
        field_label = self.order._meta.get_field('payment_fk').verbose_name
        self.assertEquals(field_label,  _('payment'))

    def test_user_fk_label(self) -> None:
        """Проверка подписи поля пользователя"""
        field_label = self.order._meta.get_field('user_fk').verbose_name
        self.assertEquals(field_label,  _('user'))

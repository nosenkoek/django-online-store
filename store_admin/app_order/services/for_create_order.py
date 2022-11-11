import logging

from decimal import Decimal
from typing import Dict

from django.contrib.auth import login
from django.db.utils import IntegrityError
from django.db import transaction
from django.db.transaction import TransactionManagementError

from app_cart.cart import Cart
from app_order.models import DeliveryMethod, Delivery, Payment, Order, \
    OrderProduct
from app_products.models import Product
from app_users.models import User

logger = logging.getLogger(__name__)


class SolveTotalPriceMixin():
    """Расчет общей суммы для оплаты с учетом доставки"""

    def get_total_price_for_payment(
            self, delivery_method: DeliveryMethod) -> Decimal:
        """
        Возвращает общую сумму с учетом стоимости доставки.
        :param delivery_method: метод доставки выбранный пользователем,
        :return: общая сумма заказа.
        """
        price_products = self._cart.get_total_price()

        if price_products >= delivery_method.free_from:
            total_price = price_products
        else:
            total_price = price_products + delivery_method.price
        return total_price


class OrderHandler(SolveTotalPriceMixin):
    """
    Обработчик заказа
    Args:
        cleaned_data: данные из формы,
        request: объект запроса,
        cart: объект заполненной корзины.
    """
    def __init__(self, cleaned_data: Dict[str, str], request, cart: Cart):
        self._cleaned_data = cleaned_data
        self._request = request
        self._cart = cart

    def _get_or_create_user(self) -> User:
        """
        Возвращает объект текущего пользователя.
        Если он не авторизован, создает его.
        :return: объект текущего пользователя
        """
        if not self._request.user.is_authenticated:
            user = User.objects.create(
                username=self._cleaned_data.get('username'),
                first_name=self._cleaned_data.get('first_name'),
                last_name=self._cleaned_data.get('last_name'),
                patronymic=self._cleaned_data.get('patronymic'),
                email=self._cleaned_data.get('email'),
                tel_number=self._cleaned_data.get('tel_number')
            )
            user.set_password(self._cleaned_data.get('password2'))
            user.save()
            return user
        return self._request.user

    def _save_products_to_order(self, order: Order, user: User) -> None:
        """
        Сохраняет товары в заказ в БД. Списывает товары со склада.
        :param order: объект заказа,
        :param user: объект текущего пользователя.
        """
        order_product, products = [], []

        for item in self._cart:
            item.product.count -= item.quantity
            products.append(item.product)
            order_product.append(OrderProduct(order_fk=order,
                                              product_fk=item.product,
                                              count=item.quantity))
        OrderProduct.objects.bulk_create(order_product)

        try:
            Product.objects.bulk_update(products, ('count',))
        except IntegrityError as err:
            logger.warning(f"Product is not availability "
                           f"for {user.username} | {err}")
            raise TransactionManagementError('Product is not availability')

        if not self._request.user.is_authenticated:
            login(self._request, user)
            logger.info(f'New user | {user.username}')

    @transaction.atomic
    def save_order(self) -> Order:
        """
        Общая атомарная транзакция для сохранения заказа.
        :return: объект заказа
        """
        user = self._get_or_create_user()

        delivery = Delivery.objects.create(
            city=self._cleaned_data.get('city'),
            address=self._cleaned_data.get('address'),
            delivery_method_fk=self._cleaned_data.get('delivery_method_fk')
        )
        payment = Payment.objects.create(
            payment_method_fk=self._cleaned_data.get('payment_method_fk')
        )
        order = Order.objects.create(
            total_price=self.get_total_price_for_payment(
                delivery.delivery_method_fk),
            delivery_fk=delivery,
            payment_fk=payment,
            user_fk=user
        )

        self._save_products_to_order(order, user)
        return order

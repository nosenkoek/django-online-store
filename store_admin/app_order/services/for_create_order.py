import logging

from decimal import Decimal

from django.contrib.auth import login
from django.db.utils import IntegrityError
from django.db import transaction
from django.db.transaction import TransactionManagementError

from app_cart.cart import Cart
from app_order.forms import CombinedFormBase
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
    def __init__(self, form_combined: CombinedFormBase, request, cart: Cart):
        self._request = request
        self._cart = cart

        for form_class in form_combined.form_classes:
            form = getattr(form_combined, form_class.__name__.lower())
            name_attr = '_'.join([form.Meta.model.__name__.lower(),
                                  'cleaned_data'])
            setattr(self, name_attr, form.cleaned_data)

    def _create_user(self) -> User:
        """
        Создание пользователя при регистрации в момент создания заказа.
        :return: объект созданного пользователя
        """
        cleaned_data_user = self.user_cleaned_data
        password = cleaned_data_user.pop('password2')
        cleaned_data_user.pop('password1')
        cleaned_data_user.pop('full_name')
        user = User.objects.create(**cleaned_data_user)
        user.set_password(password)
        user.save()
        return user

    def _get_user(self) -> User:
        """
        Возвращает объект текущего пользователя.
        Если он не авторизован, создает его.
        :return: объект текущего пользователя
        """
        if not self._request.user.is_authenticated:
            return self._create_user()
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
        user = self._get_user()

        delivery = Delivery.objects.create(**self.delivery_cleaned_data)
        payment = Payment.objects.create(**self.payment_cleaned_data)
        order = Order.objects.create(
            total_price=self.get_total_price_for_payment(
                delivery.delivery_method_fk),
            delivery_fk=delivery,
            payment_fk=payment,
            user_fk=user
        )

        self._save_products_to_order(order, user)
        return order

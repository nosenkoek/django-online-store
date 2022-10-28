from decimal import Decimal

from django.contrib.auth import login
from django.db import transaction
from django.forms import Form

from app_order.models import DeliveryMethod, Delivery, Payment, Order, \
    OrderProduct
from app_users.models import User
from app_users.services.services_views import LoginUserMixin


class SolveTotalPriceMixin():
    """Расчет общей суммы для оплаты с учетом доставки"""
    def get_total_price_for_payment(
            self, delivery_method: DeliveryMethod) -> Decimal:
        """
        Возвращает общую сумму с учетом стоимости доставки.
        :param delivery_method: метод доставки выбранный пользователем,
        :return: общая сумма заказа.
        """
        price_products = self.cart.get_total_price()

        if price_products >= delivery_method.free_from:
            total_price = price_products
        else:
            total_price = price_products + delivery_method.price
        return total_price


class SaveOrderToDbMixin(LoginUserMixin):
    """Миксин для сохранения необходимых данный в БД"""
    @staticmethod
    def _get_or_create_user(form: Form, user: User) -> User:
        if not user.is_authenticated:
            username = form.cleaned_data.get('username')
            user = User.objects.create(
                username=username,
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                patronymic=form.cleaned_data.get('patronymic'),
                email=form.cleaned_data.get('email'),
                tel_number=form.cleaned_data.get('tel_number')
            )
            user.set_password(form.cleaned_data.get('password2'))
            user.save()
        return user

    @transaction.atomic
    def save_order(self, form: Form, user: User):
        """
        Сохранение заказа в БД
        :param user: пользователь
        :param form: провалидированная форма
        """
        user = self._get_or_create_user(form, user)

        delivery = Delivery.objects.create(
            city=form.cleaned_data.get('city'),
            address=form.cleaned_data.get('address'),
            delivery_method_fk=form.cleaned_data.get('delivery_method_fk')
        )
        payment = Payment.objects.create(
            payment_method_fk=form.cleaned_data.get('payment_method_fk')
        )
        order = Order.objects.create(
            total_price=self.get_total_price_for_payment(
                delivery.delivery_method_fk),
            delivery_fk=delivery,
            payment_fk=payment,
            user_fk=user
        )
        order_product = [OrderProduct(order_fk=order,
                                      product_fk=item.product,
                                      count=item.quantity)
                         for item in self.cart]
        OrderProduct.objects.bulk_create(order_product)

        if user is not self.request.user:
            login(self.request, user)

        # todo: добавить списание товаров со склада, вопрос: в какой момент?

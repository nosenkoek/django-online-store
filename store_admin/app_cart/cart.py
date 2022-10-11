from dataclasses import dataclass
from typing import Dict, Union
from decimal import Decimal
from uuid import UUID

from django.conf import settings
from django.db.models import Sum
from django.http import HttpRequest

from app_products.models import Product


@dataclass
class CartItem():
    product: Product
    quantity: int

    def __post_init__(self):
        self.total_price = self.product.price * self.quantity
        self.availability = \
            True if self.quantity <= self.product.count else False


class Cart():
    """Корзина с товарами для покупки"""
    def __init__(self, request: HttpRequest):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def save(self):
        """ Сохранение изменений в корзине в сессии"""
        self.session.modified = True

    def add(self, product_id: UUID, quantity=1, updated=False) -> None:
        """
        Добавление товара
        :param product_id: id товара
        :param quantity: количество
        :param updated: флаг для изменения количества
        """
        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart.update({product_id: {'quantity': 1}})
        else:
            self.cart[product_id]['quantity'] += quantity

        if updated:
            self.cart[product_id]['quantity'] = quantity

        self.save()

    def delete(self, product_id: UUID) -> None:
        """
        Удаление товара из корзины.
        :param product_id: id товара
        """
        product_id = str(product_id)

        if product_id in self.cart.keys():
            self.cart.pop(product_id)
            self.save()

    def clear(self):
        """Очистка корзины"""
        self.session.pop(settings.CART_SESSION_ID)
        self.save()

    def __iter__(self) -> CartItem:
        for product_id, item in self.cart.items():
            # todo: придумать как перевести на QS
            product = Product.objects.get(product_id=product_id)
            yield CartItem(product=product,
                           quantity=item.get('quantity'))

    def __len__(self) -> int:
        """
        Количество товаров в корзине.
        :return: количество товаров
        """
        return len(self.cart.keys())

    def get_total_price(self) -> Decimal:
        """
        Получение общей стоимости товаров.
        :return: общая стоимость
        """
        product_ids = self.cart.keys()
        total_dict = Product.objects.filter(product_id__in=product_ids)\
            .aggregate(total=Sum('price'))
        return total_dict.get('total')

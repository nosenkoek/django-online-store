from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.conf import settings
from django.http import HttpRequest

from app_products.models import Product


@dataclass
class CartItem():
    """Объект хранимый в корзине"""
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

    def remove(self, product_id: UUID) -> None:
        """
        Удаление 1 товара из корзины.
        :param product_id: id товара
        """
        product_id_str = str(product_id)

        if product_id_str in self.cart.keys():
            if self.cart[product_id_str]['quantity'] <= 1:
                self.delete_all(product_id)
            else:
                self.cart[product_id_str]['quantity'] -= 1
                self.save()

    def delete_all(self, product_id: UUID) -> None:
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
        products = Product.objects.filter(product_id__in=self.cart.keys())

        for product in products:
            quantity = self.cart.get(str(product.product_id)).get('quantity')
            yield CartItem(product=product,
                           quantity=quantity)

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
        return sum([item.total_price for item in self])

    def get_quantity(self, product_id: UUID) -> int:
        """
        Возвращает количество товаров по product_id
        :param product_id: id товара
        :return: количество товаров в корзине
        """
        data_product = self.cart.get(str(product_id))
        if data_product:
            return data_product.get('quantity')
        return 0

    def check_availability(self) -> bool:
        """
        Проверка корзины на наличие товаров на складе.
        """
        for item in self:
            if not item.availability:
                return False
        return True

from decimal import Decimal
from typing import Dict

from app_cart.cart import Cart


class GetContextTotalPriceCartMixin():
    """Миксин для добавления контекста о корзине"""
    def get_context_price_cart(self) -> Dict[str, Decimal]:
        """
        Возвращает словарь для добавления во View в виде контекста
        :return: словарь с данными о корзине
        """
        cart = Cart(self.request)
        context_data = {
            'total_price_cart': cart.get_total_price(),
            'count_product_cart': len(cart)
        }
        return context_data


class CartRequestMixin():
    """Миксин для добавления объекта корзина в атрибуты"""
    @property
    def cart(self) -> Cart:
        return Cart(self.request)


class NextURLRequestMixin():
    """Миксин для добавления страницы перехода в атрибуты"""
    @property
    def next_url(self) -> str:
        return self.request.GET['next']

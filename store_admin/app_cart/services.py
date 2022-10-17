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

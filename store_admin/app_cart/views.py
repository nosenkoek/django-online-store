from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, ListView

from app_cart.cart import Cart
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_products.models import Product


class CartView(TemplateView):
    template_name = 'app_cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        cart = Cart(self.request)
        context.update({'cart': cart})
        context.update(NaviCategoriesList().get_context())
        return context


class AddProductCartView(View):
    """Представление для добавления товаров со страниц с товарами"""
    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        next_url = request.GET['next']
        cart = Cart(request)
        cart.add(product_id)
        return redirect(next_url)


class DeleteProductCartView(View):
    """Представление для удаления товаров из корзины"""
    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        cart = Cart(request)
        cart.delete(product_id)
        return redirect('cart')

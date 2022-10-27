from typing import Dict

from django.views.generic import FormView

from app_cart.cart import Cart
from app_cart.services.mixins_for_cart import GetContextTotalPriceCartMixin
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_order.forms import CheckoutForm
from app_users.models import User
from app_users.services.services_views import InitialDictMixin


class CheckoutView(FormView, GetContextTotalPriceCartMixin, InitialDictMixin):
    form_class = CheckoutForm
    template_name = 'app_order/checkout.html'
    success_url = '/users/account'

    def get_initial(self) -> Dict[str, str]:
        if self.request.user.is_authenticated:
            return self.get_initial_form(self.request.user)
        return {}

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        cart = Cart(self.request)
        context.update({'cart': cart})
        return context

    def get_form_kwargs(self):
        user = User.objects.get(id=self.request.user.id)
        kwargs = super(CheckoutView, self).get_form_kwargs()
        kwargs.update({'instance': user})
        return kwargs

    def form_valid(self, form):
        result = super(CheckoutView, self).form_valid(form)
        print(result)
        return result

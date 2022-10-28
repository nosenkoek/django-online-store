from typing import Dict

from django.views.generic import FormView

from app_cart.services.mixins_for_cart import GetContextTotalPriceCartMixin, \
    CartRequestMixin
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_order.forms import CheckoutForm
from app_order.services.for_create_order import SolveTotalPriceMixin, \
    SaveOrderToDbMixin
from app_users.models import User
from app_users.services.services_views import InitialDictMixin


class CheckoutView(FormView, GetContextTotalPriceCartMixin, InitialDictMixin,
                   CartRequestMixin, SolveTotalPriceMixin, SaveOrderToDbMixin):
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
        context.update({'cart': self.cart})
        return context

    def get_form_kwargs(self):
        kwargs = super(CheckoutView, self).get_form_kwargs()
        if self.request.user.is_authenticated:
            user = User.objects.get(id=self.request.user.id)
            kwargs.update({'instance': user})
        return kwargs

    def form_valid(self, form):
        result = super(CheckoutView, self).form_valid(form)
        print(form.cleaned_data)
        self.save_order(form, self.request.user)
        self.cart.clear()
        return result

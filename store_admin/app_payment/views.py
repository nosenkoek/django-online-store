from typing import Dict

from django.urls import reverse
from django.views.generic import TemplateView, RedirectView, FormView

from app_cart.services.mixins_for_cart import GetContextTotalPriceCartMixin
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_order.models import Order
from app_payment.forms import FormCard, FormAccount


class PayView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        order_id = kwargs.get('order_id')
        order = Order.objects.select_related('payment_fk')\
            .get(order_id=order_id)
        if order.payment_fk.payment_method == 'card':
            return reverse('payment_card', args=(order_id, ))
        return reverse('payment_account', args=(order_id, ))


class BasePaymentView(TemplateView, GetContextTotalPriceCartMixin):
    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context


class BasePaymentFormView(FormView, GetContextTotalPriceCartMixin):
    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        order_id = self.kwargs.get('order_id')
        print(order_id)
        return result

    def get_success_url(self):
        return reverse('payment_progress')


class PaymentProgressView(BasePaymentView):
    template_name = 'app_payment/payment_progress.html'


class PaymentCardView(BasePaymentFormView):
    template_name = 'app_payment/payment_card.html'
    form_class = FormCard


class PaymentAccountView(BasePaymentFormView):
    template_name = 'app_payment/payment_account.html'
    form_class = FormAccount

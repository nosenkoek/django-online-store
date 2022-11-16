from datetime import datetime, timedelta
from typing import Dict

from celery.result import AsyncResult
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView, FormView
from django.http import JsonResponse

from app_cart.services.mixins_for_cart import GetContextTotalPriceCartMixin
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_order.models import Order
from app_payment.forms import FormPayment
from app_payment.tasks import payment_task

# TODO:
#  1. рефакторинг + написать докстринги
#  2. Посмотреть админку подробнее, м.б. доработать
#  3. дописать логи при оплате
#  4. сделать докер + расшарить папку log через nginx
#  5. может переделать на 1 вьюху оплата картой/ по счету
#  6. дописать тесты


class PayView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        order_id = kwargs.get('order_id')
        order = Order.objects.select_related('payment_fk') \
            .get(order_id=order_id)
        if order.payment_fk.payment_method == 'card':
            return reverse('payment_card', args=(order_id,))
        return reverse('payment_account', args=(order_id,))


class BasePaymentFormView(FormView, GetContextTotalPriceCartMixin):
    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        order_id = self.kwargs.get('order_id')
        number = form.cleaned_data.get('number')
        res = AsyncResult(order_id)
        if res:
            res.forget()
        payment_task.apply_async((order_id, number), task_id=order_id)
        return result

    def get_success_url(self):
        return reverse('payment_progress',
                       args=(self.kwargs.get('order_id'),))


class PaymentCardView(BasePaymentFormView):
    template_name = 'app_payment/payment_card.html'
    form_class = FormPayment


class PaymentAccountView(BasePaymentFormView):
    template_name = 'app_payment/payment_account.html'
    form_class = FormPayment


class PaymentProgressView(TemplateView, GetContextTotalPriceCartMixin):
    template_name = 'app_payment/payment_progress.html'

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(PaymentProgressView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')

        if request.is_ajax():
            result = AsyncResult(order_id)

            if result.ready():
                order_number = Order.objects.get(order_id=order_id).number
                return JsonResponse({
                    'success': True,
                    'url': reverse('order_detail', args=(order_number,)),
                })
            # todo: добавить timeout для остановки оплаты и ошибки
            #  (можно через counter)
        return super(PaymentProgressView, self).get(request, *args, **kwargs)

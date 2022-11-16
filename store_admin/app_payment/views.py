import logging
from typing import Dict

from celery.result import AsyncResult
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.http import JsonResponse

from app_cart.services.mixins_for_cart import GetContextTotalPriceCartMixin
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_order.models import Order
from app_payment.forms import FormPayment
from app_payment.tasks import payment_task

# TODO:
#  4. сделать докер + расшарить папку log через nginx
#  6. дописать тесты

logger = logging.getLogger(__name__)


class PaymentView(FormView, GetContextTotalPriceCartMixin):
    """View для оплаты"""
    template_name = 'app_payment/payment_form.html'
    form_class = FormPayment

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        order_id = self.kwargs.get('order_id')
        payment_method = Order.objects.get(order_id=order_id)\
            .payment_fk.payment_method
        context.update({'payment_method': payment_method})
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


class PaymentProgressView(TemplateView, GetContextTotalPriceCartMixin):
    """View для ожидания оплаты"""
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

            if result and result.ready():
                order = Order.objects.select_related('payment_fk')\
                    .get(order_id=order_id)

                if order.payment_fk.paid:
                    logger.info(f'Paid order {order_id}')
                else:
                    logger.warning(f'Unpaid order {order.order_id} | '
                                   f'{order.payment_fk.error}')

                return JsonResponse({
                    'success': True,
                    'url': reverse('order_detail', args=(order.number,)),
                })
            # todo: добавить timeout для остановки оплаты и ошибки
            #  (можно через counter)
        return super(PaymentProgressView, self).get(request, *args, **kwargs)

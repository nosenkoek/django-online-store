import logging
from typing import Dict

from django.contrib import messages
from django.db.models import QuerySet
from django.db.transaction import TransactionManagementError
from django.views.generic import FormView, ListView, DetailView

from app_cart.services.mixins_for_cart import GetContextTotalPriceCartMixin, \
    CartRequestMixin
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_order.forms import CheckoutForm
from app_order.models import Order, OrderProduct
from app_order.services.for_create_order import OrderHandler
from app_users.models import User
from app_users.services.services_views import InitialDictMixin, LoginUserMixin

logger = logging.getLogger(__name__)


class CheckoutView(FormView, GetContextTotalPriceCartMixin, InitialDictMixin,
                   CartRequestMixin, LoginUserMixin):
    """Представление для оформления заказа"""
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
        order_handler = OrderHandler(cart=self.cart, request=self.request,
                                     form_combined=form)
        try:
            order = order_handler.save_order()
        except TransactionManagementError as err:
            logger.warning(f'Not save order | {err}')
            messages.error(self.request, f"Order wasn't created. {err}")
            return self.form_invalid(form)
        else:
            logger.info(f'Order {order.id} created')

        self.cart.clear()
        return result


class OrderHistoryListView(ListView, GetContextTotalPriceCartMixin):
    model = Order
    template_name = 'app_order/order_history.html'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(OrderHistoryListView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context

    def get_queryset(self) -> QuerySet:
        queryset = super(OrderHistoryListView, self).get_queryset() \
            .filter(user_fk=self.request.user).order_by('-created') \
            .select_related('delivery_fk', 'delivery_fk__delivery_method_fk',
                            'payment_fk', 'payment_fk__payment_method_fk')
        return queryset


class OrderDetailView(DetailView, GetContextTotalPriceCartMixin):
    model = Order
    template_name = 'app_order/order_detail.html'
    context_object_name = 'order'
    slug_field = 'number'
    slug_url_kwarg = 'number'

    def get_queryset(self):
        queryset = super(OrderDetailView, self).get_queryset()
        queryset = queryset.select_related('user_fk', 'delivery_fk',
                                           'delivery_fk__delivery_method_fk',
                                           'payment_fk',
                                           'payment_fk__payment_method_fk')
        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())

        order_products = OrderProduct.objects \
            .filter(order_fk=self.get_object()).select_related('product_fk')
        context.update({'order_products': order_products})
        return context

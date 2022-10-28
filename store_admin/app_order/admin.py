from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from app_order.models import DeliveryMethod, PaymentMethod, Order, \
    OrderProduct, Delivery, Payment


class OrderProductInline(admin.TabularInline):
    """Inline товаров в заказах"""
    model = OrderProduct
    fields = ('product_fk', 'count')
    extra = 0

    def has_add_permission(self, request, obj) -> bool:
        """Возможность добавлять товары"""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Возможность удалять товары"""
        return False

    def has_change_permission(self, request, obj=None):
        """Возможность менять товары"""
        return False


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'free_from')
    search_fields = ('name',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('city', 'address', 'delivery_method_fk')
    search_fields = ('city',)
    list_filter = ('delivery_method_fk',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    # todo: перенести в app_payment
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # todo: перенести в app_payment
    list_display = ('status_payment', 'error', 'payment_method_fk')
    list_filter = ('status_payment', 'payment_method_fk')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user_fk', 'total_price', 'status_payment', 'created',
                    'to_city', 'to_address', 'delivery_method')
    readonly_fields = list_display
    list_filter = ('payment_fk__status_payment',)
    list_select_related = ('payment_fk', 'delivery_fk', 'user_fk',
                           'delivery_fk__delivery_method_fk')

    inlines = (OrderProductInline,)

    @admin.display(description=_('payment status'))
    def status_payment(self, obj):
        return obj.payment_fk.status_payment

    status_payment.boolean = True

    @admin.display(description=_('delivery city'))
    def to_city(self, obj):
        return obj.delivery_fk.city

    @admin.display(description=_('delivery address'))
    def to_address(self, obj):
        return obj.delivery_fk.address

    @admin.display(description=_('delivery method'))
    def delivery_method(self, obj):
        result = '<a href="{}">{}</a>'.format(
            reverse('admin:app_order_delivery_change',
                    args=(obj.delivery_fk.id, )),
            obj.delivery_fk.delivery_method_fk)
        return mark_safe(result)

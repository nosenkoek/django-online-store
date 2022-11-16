from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from app_payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'payment_method', 'error', 'paid')
    list_filter = ('paid', 'payment_method')

    @admin.display(description=_('order number'))
    def order_number(self, obj):
        return obj.order.number

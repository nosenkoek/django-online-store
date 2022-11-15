from django.contrib import admin

from app_payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_method', 'error', 'paid')
    list_filter = ('paid', 'payment_method')

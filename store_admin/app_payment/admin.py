from django.contrib import admin

from app_payment.models import PaymentMethod, Payment


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_method_fk', 'error', 'paid')
    list_filter = ('paid', 'payment_method_fk')

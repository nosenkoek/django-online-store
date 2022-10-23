from django.contrib import admin

from app_order.models import DeliveryMethod, PaymentMethod


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'free_from')
    search_fields = ('name', )


@admin.register(PaymentMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    # todo: перенести в app_payment
    list_display = ('name', )
    search_fields = ('name',)

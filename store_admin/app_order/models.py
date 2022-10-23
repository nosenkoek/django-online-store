from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class DeliveryMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    method_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30, verbose_name=_('name'))
    price = models.DecimalField(max_digits=7, decimal_places=2,
                                verbose_name=_('price'),
                                validators=[MinValueValidator(0)])
    free_from = models.PositiveIntegerField(verbose_name=_('price_free_from'))

    class Meta:
        managed = False
        db_table = 'delivery_method'
        verbose_name = _('delivery method')
        verbose_name_plural = _('delivery methods')

    def __str__(self):
        return f'{self.name}. Цена {self.price}₽. ' \
               f'Бесплатно при заказе от {self.free_from}₽'


class Delivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    delivery_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    city = models.CharField(max_length=50, verbose_name=_('city'))
    address = models.TextField(verbose_name=_('address'))
    delivery_method_fk = models.ForeignKey(DeliveryMethod,
                                           on_delete=models.CASCADE,
                                           to_field='method_id',
                                           db_column='delivery_method_fk',
                                           verbose_name=_('delivery method'))

    class Meta:
        managed = False
        db_table = 'delivery'
        verbose_name = _('delivery')
        verbose_name_plural = _('deliveries')


class PaymentMethod(models.Model):
    # todo: перенести в app_payment
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    method_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    name = models.CharField(max_length=40, verbose_name=_('payment method'))

    class Meta:
        managed = False
        db_table = 'payment_method'
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')

    def __str__(self):
        return self.name


class Payment(models.Model):
    # todo: перенести в app_payment
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    payment_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    status_payment = models.BooleanField()
    error = models.TextField(blank=True, null=True)
    payment_method_fk = models.ForeignKey(PaymentMethod,
                                          on_delete=models.CASCADE,
                                          to_field='method_id',
                                          db_column='payment_method_fk',
                                          verbose_name=_('payment'))

    class Meta:
        managed = False
        db_table = 'payment'
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

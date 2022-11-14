from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    method_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    name = models.CharField(max_length=40, verbose_name=_('name'))

    class Meta:
        managed = False
        db_table = 'payment_method'
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')

    def __str__(self):
        return self.name


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    payment_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    paid = models.DateTimeField(blank=True, null=True,
                                verbose_name=_('date of paid'))
    error = models.TextField(blank=True, null=True, verbose_name=_('error'))
    payment_method_fk = models.ForeignKey(PaymentMethod,
                                          on_delete=models.CASCADE,
                                          to_field='method_id',
                                          db_column='payment_method_fk',
                                          verbose_name=_('payment'),
                                          default=PaymentMethod.objects
                                          .first())

    class Meta:
        managed = False
        db_table = 'payment'
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return _('Paid: {}').format(self.paid)

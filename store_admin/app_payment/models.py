from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    class Method(models.TextChoices):
        CARD = 'card', _('Card')
        ACCOUNT = 'account', _('Bank account')

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    payment_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    paid = models.DateTimeField(blank=True, null=True,
                                verbose_name=_('date of paid'))
    error = models.TextField(blank=True, null=True, verbose_name=_('error'))
    payment_method = models.CharField(max_length=30,
                                      choices=Method.choices,
                                      default=Method.CARD,
                                      verbose_name=_('payment method'))

    class Meta:
        managed = False
        db_table = 'payment'
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        if self.paid:
            msg = _('Paid: {}').format(self.paid)
        else:
            msg = _('Unpaid').format(self.paid)
        return msg

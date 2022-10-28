from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from app_products.models import Product
from app_users.models import User


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
        return _('{}. Price {}₽. Free from {}₽').format(self.name,
                                                        self.price,
                                                        self.free_from)


class Delivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    delivery_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    city = models.CharField(max_length=50, verbose_name=_('city'))
    address = models.TextField(verbose_name=_('address'))

    delivery_method_fk = models.ForeignKey(DeliveryMethod,
                                           on_delete=models.CASCADE,
                                           to_field='method_id',
                                           db_column='delivery_method_fk',
                                           verbose_name=_('delivery method'),
                                           default=DeliveryMethod.objects
                                           .first())

    class Meta:
        managed = False
        db_table = 'delivery'
        verbose_name = _('delivery')
        verbose_name_plural = _('deliveries')

    def __str__(self):
        return _('Delivery to {}.').format(self.city)


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
    status_payment = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)
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
        return _('Paid: {}').format(self.status_payment)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    order_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=_('created'))
    total_price = models.DecimalField(max_digits=7, decimal_places=2,
                                      verbose_name=_('total price'),
                                      validators=[MinValueValidator(0)])

    delivery_fk = models.OneToOneField(Delivery,
                                       on_delete=models.CASCADE,
                                       to_field='delivery_id',
                                       db_column='delivery_fk',
                                       verbose_name=_('delivery'),
                                       editable=False)
    payment_fk = models.OneToOneField(Payment,
                                      on_delete=models.CASCADE,
                                      to_field='payment_id',
                                      db_column='payment_fk',
                                      verbose_name=_('payment'),
                                      editable=False)
    user_fk = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                to_field='id',
                                db_column='user_fk',
                                verbose_name=_('user'))

    products = models.ManyToManyField(Product, through='OrderProduct')

    class Meta:
        managed = False
        db_table = 'order'
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return _('Order for {}').format(self.user_fk)


class OrderProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    count = models.IntegerField(validators=[MinValueValidator(0)])

    order_fk = models.ForeignKey(Order,
                                 on_delete=models.CASCADE,
                                 to_field='order_id',
                                 db_column='order_fk',
                                 verbose_name=_('order'))

    product_fk = models.ForeignKey(Product,
                                   on_delete=models.CASCADE,
                                   to_field='product_id',
                                   db_column='product_fk',
                                   verbose_name=_('product'))

    class Meta:
        managed = False
        db_table = 'order_product'
        unique_together = (('order_fk', 'product_fk'),)
        verbose_name = _('products in order')
        verbose_name_plural = _('products in orders')

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from app_products.models import Product


class Profile(models.Model):
    """Дополнительная информация о пользователях"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    profile_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    tel_number = models.CharField(max_length=10, unique=True,
                                  verbose_name=_('telephone number'))
    patronymic = models.CharField(max_length=30,
                                  verbose_name=_('patronymic'))
    avatar = models.ImageField(upload_to='avatars/', null=True,
                               verbose_name=_('avatar'))

    user_fk = models.OneToOneField(User,
                                   on_delete=models.CASCADE,
                                   verbose_name=_('user'))

    class Meta:
        managed = False
        db_table = 'profile'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')


class Feedback(models.Model):
    """Отзывы о товарах от пользователей"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    feedback_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    text = models.TextField(verbose_name=_('text'))
    added = models.DateTimeField(auto_now_add=True, verbose_name=_('added'))

    product_fk = models.ForeignKey(Product,
                                   on_delete=models.CASCADE,
                                   to_field='product_id',
                                   db_column='product_fk',
                                   verbose_name=_('product'))
    user_fk = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                verbose_name=_('user'))

    class Meta:
        managed = False
        db_table = 'feedback'
        verbose_name = _('feedback')
        verbose_name_plural = _('feedbacks')

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from app_products.models import Product

SIZE_IMAGE_MAX_MB = 2


def file_size_validator(file):
    if file:
        size_mb = round(file.size / (1024 * 1024), 2)
        if size_mb > SIZE_IMAGE_MAX_MB:
            raise ValidationError(_('File size is {}Mb. '
                                    'Should not be more than 2Mb')
                                  .format(size_mb))


class Profile(models.Model):
    """Дополнительная информация о пользователях"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    profile_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    tel_number = models.CharField(max_length=10, unique=True,
                                  verbose_name=_('telephone number'))
    patronymic = models.CharField(max_length=30, null=True, blank=True,
                                  verbose_name=_('patronymic'))
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True,
                               validators=(file_size_validator, ),
                               verbose_name=_('avatar'))

    user_fk = models.OneToOneField(User,
                                   on_delete=models.CASCADE,
                                   to_field='id',
                                   db_column='user_fk_id',
                                   verbose_name=_('user'))

    class Meta:
        managed = False
        db_table = 'profile'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return self.user_fk.username


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
                                to_field='id',
                                db_column='user_fk_id',
                                verbose_name=_('user'))

    class Meta:
        managed = False
        db_table = 'feedback'
        verbose_name = _('feedback')
        verbose_name_plural = _('feedbacks')

    def __str__(self):
        return self.text[:15]

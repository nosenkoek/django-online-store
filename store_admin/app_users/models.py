from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

SIZE_IMAGE_MAX_MB = 2


def file_size_validator(file):
    if file:
        size_mb = round(file.size / (1024 * 1024), 2)
        if size_mb > SIZE_IMAGE_MAX_MB:
            raise ValidationError(_('File size is {}Mb. '
                                    'Should not be more than 2Mb')
                                  .format(size_mb))


class User(AbstractUser):
    tel_number = models.CharField(max_length=10, unique=True,
                                  validators=[MinLengthValidator(10)],
                                  verbose_name=_('telephone number'))
    patronymic = models.CharField(max_length=30, null=True, blank=True,
                                  verbose_name=_('patronymic'))
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True,
                               validators=(file_size_validator, ),
                               verbose_name=_('avatar'))

    def get_full_name(self):
        if self.patronymic is None:
            return f'{self.last_name} {self.first_name}'
        return f'{self.last_name} {self.first_name} {self.patronymic}'

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app_users.models import file_size_validator, User


class AddValidationFullNameMixin():
    """Миксин для валидации ФИО"""
    def clean_full_name(self) -> str:
        """
        Метод проверки и преобразования ФИО
        :return: ФИО
        """
        full_name = self.cleaned_data.pop('full_name')
        full_name_words = full_name.split()

        length_name = len(full_name_words)

        if length_name == 2:
            self.cleaned_data.update({
                'last_name': full_name_words[0],
                'first_name': full_name_words[1]
            })
        elif length_name == 3:
            self.cleaned_data.update({
                'last_name': full_name_words[0],
                'first_name': full_name_words[1],
                'patronymic': full_name_words[2]
            })
        else:
            raise ValidationError(_('Enter full name. First name, '
                                    'last name and patronymic'))
        return full_name


class AddValidatorPasswordMixin():
    """Миксин для валидации password"""
    def clean_password2(self) -> str:
        """
        Валидация введенных паролей.
        :return: пароль
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            password_validation.validate_password(password2, self.instance)
            if password1 != password2:
                raise ValidationError(
                    _('The two password fields didn’t match.'),
                    code='password_mismatch',
                )
        return password2


class AddValidatorEmailMixin():
    """Миксин для валидации email"""
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if (email != self.instance.email and
                User.objects.filter(email=email).exists()):
            raise ValidationError(_('Profile with this Email already exists.'))
        return email


class AddValidationAvatarMixin():
    """Миксин для валидации аватара"""
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        file_size_validator(avatar)
        return avatar

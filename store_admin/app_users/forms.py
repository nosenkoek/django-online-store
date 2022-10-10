from django.contrib.auth import password_validation
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app_users.models import file_size_validator, User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    """Форма для регистрации пользователя"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'patronymic',
                  'email', 'tel_number', 'password1', 'password2')

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Profile with this Email already exists.'))
        return email


class AddValidationFieldsMixin():
    """Миксин для добавления дополнительных валидаций полей"""
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if (email != self.instance.email and
                User.objects.filter(email=email).exists()):
            raise ValidationError(_('Profile with this Email already exists.'))
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        file_size_validator(avatar)
        return avatar


class UserProfileForm(forms.ModelForm, AddValidationFieldsMixin):
    """Форма для редактирования профиля пользователя"""
    full_name = forms.CharField(
        label=_('Full name. Last name, first name, patronymic')
    )
    password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=False
    )
    password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False
    )

    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'patronymic',
                  'tel_number', 'email', 'password1', 'password2')

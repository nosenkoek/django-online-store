from django.contrib.auth import password_validation
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app_users.models import User
from django.contrib.auth.forms import UserCreationForm

from app_users.services.validators_forms_mixins import \
    AddValidationFullNameMixin, AddValidatorPasswordMixin, \
    AddValidatorEmailMixin, AddValidationAvatarMixin


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


class UserProfileForm(forms.ModelForm, AddValidationFullNameMixin,
                      AddValidatorPasswordMixin, AddValidatorEmailMixin,
                      AddValidationAvatarMixin):
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

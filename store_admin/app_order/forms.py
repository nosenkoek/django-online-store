from django import forms
from django.contrib.auth import password_validation
from django.utils.translation import gettext as _

from app_users.services.validators_forms_mixins \
    import AddValidationFullNameMixin, AddValidatorEmailMixin, \
    AddValidatorPasswordMixin
from app_users.models import User


class CheckoutForm(forms.ModelForm, AddValidationFullNameMixin,
                   AddValidatorEmailMixin, AddValidatorPasswordMixin):
    """Форма для оформления заказа"""
    full_name = forms.CharField(
        label=_('Last name, first name, patronymic')
    )

    password1 = forms.CharField(
        label=_("Enter password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=False
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'password'}),
        required=False
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic',
                  'email', 'tel_number', 'password1', 'password2')




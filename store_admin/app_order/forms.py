from django import forms
from django.contrib.auth import password_validation
from django.utils.translation import gettext as _

from app_order.models import Delivery, Payment
from app_users.services.validators_forms_mixins \
    import AddValidationFullNameMixin, AddValidatorEmailMixin, \
    AddValidatorPasswordMixin
from app_users.models import User


class GetFormMixin():
    """Миксин для возврата формы из form_classes в CombinedFormBase"""
    def _get_current_form(self, form_class: forms.Form) -> forms.Form:
        """
        Возвращает текущую форму.
        :param form_class: класс из списка объектов форм form_classes,
        :return: объект текущей формы из списка form_classes.
        """
        name = form_class.__name__.lower()
        return getattr(self, name)


class CombinedFormBase(forms.Form, GetFormMixin):
    """Базовая форма для объединения различных ModelForm"""
    form_classes = []

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance') if 'instance' in kwargs.keys() \
            else None

        super(CombinedFormBase, self).__init__(*args, **kwargs)
        for form_class in self.form_classes:
            name = form_class.__name__.lower()
            kwargs.update({'instance': instance})
            setattr(self, name, form_class(*args, **kwargs))
            form = getattr(self, name)
            self.fields.update(form.fields)
            self.initial.update(form.initial)

    def is_valid(self) -> bool:
        flag_is_valid = True

        for form_class in self.form_classes:
            form = self._get_current_form(form_class)
            if not form.is_valid():
                flag_is_valid = False

        if not super(CombinedFormBase, self).is_valid():
            flag_is_valid = False

        for form_class in self.form_classes:
            form = self._get_current_form(form_class)
            self.errors.update(form.errors)
        return flag_is_valid

    def clean(self):
        cleaned_data = super(CombinedFormBase, self).clean()
        for form_class in self.form_classes:
            form = self._get_current_form(form_class)
            cleaned_data.update(form.cleaned_data)
        return cleaned_data


class CheckoutUserForm(forms.ModelForm, AddValidationFullNameMixin,
                       AddValidatorEmailMixin, AddValidatorPasswordMixin):
    """Форма для оформления заказа. Шаг 1. Пользователь"""
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
        fields = ('first_name', 'last_name', 'patronymic', 'email',
                  'tel_number', 'password1', 'password2', 'username')


class CheckoutDeliveryForm(forms.ModelForm):
    """Форма для оформления заказа. Шаг 2. Доставка"""
    class Meta:
        model = Delivery
        fields = ('city', 'address', 'delivery_method_fk')

        widgets = {
            'delivery_method_fk': forms.RadioSelect(
                attrs={'class': 'radio_select',
                       "required": "required"})
        }


class CheckoutPaymentForm(forms.ModelForm):
    """Форма для оформления заказа. Шаг 3. Оплата"""
    class Meta:
        model = Payment
        fields = ('payment_method',)

        widgets = {
            'payment_method': forms.RadioSelect(
                attrs={'class': 'radio_select',
                       "required": "required"})
        }


class CheckoutForm(CombinedFormBase):
    """Объединенная форма для оформления заказа"""
    form_classes = [CheckoutUserForm, CheckoutDeliveryForm,
                    CheckoutPaymentForm]

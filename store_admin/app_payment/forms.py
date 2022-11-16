from django import forms
from django.core.exceptions import ValidationError


class FormPayment(forms.Form):
    number = forms.CharField(min_length=9, max_length=9,
                             widget=forms.TextInput(attrs={
                                 'class': 'form-input Payment-bill',
                                 'placeholder': "9999 9999",
                                 'data-mask': "9999 9999"
                             }))

    def clean_number(self) -> str:
        number = self.cleaned_data.get('number')
        number = number.replace(' ', '')
        try:
            int(number)
        except ValueError:
            raise ValidationError('Please enter right format for account '
                                  '(only digits).')
        return number

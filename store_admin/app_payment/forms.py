from django import forms


class FormCard(forms.Form):
    number_card = forms.CharField(min_length=9, max_length=9,
                                  widget=forms.TextInput(attrs={
                                      'class': 'form-input Payment-bill',
                                      'placeholder': "9999 9999",
                                      'data-mask': "9999 9999"
                                  }))


class FormAccount(forms.Form):
    number_account = forms.CharField(min_length=9, max_length=9,
                                     widget=forms.TextInput(attrs={
                                         'class': 'form-input Payment-bill',
                                         'placeholder': "9999 9999",
                                         'data-mask': "9999 9999"
                                     }))

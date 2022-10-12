from django import forms


class CartAddProductForm(forms.Form):
    """Форма для изменения количества товаров в корзине"""
    quantity = forms.IntegerField()
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)

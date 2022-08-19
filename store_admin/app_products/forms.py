from django import forms
from django.utils.translation import gettext_lazy as _

from app_products.models import Product

FeatureInlineFormset = forms.inlineformset_factory(Product,
                                                   Product.features.through,
                                                   exclude=[])


class FeatureFormset(FeatureInlineFormset):
    """Формсет для инлайнов в товарах"""

    # todo: сделать класс choice
    def add_fields(self, form, index) -> None:
        """Добавление виджета RadioSelect для характеристик типа checkbox"""
        if index is not None and \
                form.instance.feature_fk.type_feature == 'checkbox':
            form.fields['value'] = forms.ChoiceField(
                widget=forms.RadioSelect,
                choices=[('no', _('no')), ('yes', _('yes'))]
            )
        super().add_fields(form, index)

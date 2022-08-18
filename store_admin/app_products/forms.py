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



class FilterProductForm(forms.Form):
    #todo: потом удалить,если не используется
    price = forms.CharField(label=_('price'))
    name = forms.CharField(label=_('name'), required=False)
    available = forms.BooleanField(label=_('available'), required=False)

    def __init__(self, *args, **kwargs):
        features = kwargs.pop('features')
        super(FilterProductForm, self).__init__(*args, **kwargs)

        for feature in features:
            if feature.type_feature == 'checkbox':
                self.fields.update({
                    str(feature.feature_id): forms.BooleanField(
                        widget=forms.CheckboxInput,
                        label=feature.name,
                        required=False)
                })
            elif feature.type_feature == 'select':
                value_choices = (
                    (product_feature.value, product_feature.value)
                    for product_feature in feature.productfeature_set.all()
                )

                self.fields.update({
                    str(feature.feature_id): forms.MultipleChoiceField(
                        label=feature.name,
                        choices=value_choices,
                        required=False)
                })
            else:
                self.fields.update({
                    str(feature.feature_id): forms.CharField(
                        label=feature.name,
                        required=False)
                })

    def clean(self):
        """В cleaned_data добавляются только заполненные поля"""
        cleaned_data = super(FilterProductForm, self).clean()

        cleaned_data = {name: value
                        for name, value in cleaned_data.items()
                        if name in self.changed_data}

        price_str = cleaned_data.get('price')

        try:
            price_range = [float(data) for data in price_str.split(';')]
        except TypeError:
            # todo: logger
            raise TypeError('Ошибка в фильтрации цены')
        cleaned_data.update({'price': price_range})
        return cleaned_data

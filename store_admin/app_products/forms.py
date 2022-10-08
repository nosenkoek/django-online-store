from django import forms
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from app_products.models import Product, Feedback

FeatureInlineFormset = forms.inlineformset_factory(Product,
                                                   Product.features.through,
                                                   exclude=[])


class FeatureFormset(FeatureInlineFormset):
    """Формсет для инлайнов в товарах"""
    class CheckboxFeature(TextChoices):
        NO = 'no', _('no')
        YES = 'yes', _('yes')

    def add_fields(self, form, index) -> None:
        """Добавление виджета RadioSelect для характеристик типа checkbox"""
        if index is not None and \
                form.instance.feature_fk.type_feature == 'checkbox':
            form.fields['value'] = forms.ChoiceField(
                widget=forms.RadioSelect,
                choices=self.CheckboxFeature.choices
            )
        super().add_fields(form, index)


class FeedbackNewForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text', )

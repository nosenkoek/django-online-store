from abc import ABC
from typing import Tuple

from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet


class InputFilterAdmin(ABC, SimpleListFilter):
    """Абстрактный класс для фильтра вида text input"""

    template = 'admin_custom/input_filter.html'

    def lookups(self, request, model_admin) -> Tuple[Tuple]:
        return (('', ''),)

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (name, value)
            for name, value in changelist.get_filters_params().items()
            if name != self.parameter_name
        )
        yield all_choice


class ProductCategoryFilterAdmin(InputFilterAdmin):
    """Фильтр для товаров по категории"""

    title = _('category')
    parameter_name = 'category'

    def queryset(self, request, queryset) -> QuerySet:
        if self.value():
            category_name = self.value()
            queryset = queryset.filter(category_fk__name=category_name)
            return queryset


class ProductManufacturerFilterAdmin(InputFilterAdmin):
    """Фильтр для товаров по производителю"""

    title = _('manufacturer')
    parameter_name = 'manufacturer'

    def queryset(self, request, queryset) -> QuerySet:
        if self.value():
            manufacturer_name = self.value()
            queryset = queryset.filter(manufacturer_fk__name=manufacturer_name)
            return queryset


class FeedbackProductFilterAdmin(InputFilterAdmin):
    """Фильтр для отзывов по товарам"""
    title = _('product')
    parameter_name = 'product'

    def queryset(self, request, queryset) -> QuerySet:
        if self.value():
            product_name = self.value()
            queryset = queryset.filter(product_fk__name=product_name)
            return queryset


class FeedbackUsernameFilterAdmin(InputFilterAdmin):
    """Фильтр для отзывов по товарам"""
    title = _('username')
    parameter_name = 'username'

    def queryset(self, request, queryset) -> QuerySet:
        if self.value():
            username = self.value()
            queryset = queryset.filter(user_fk__username=username)
            return queryset

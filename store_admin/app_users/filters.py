from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from app_products.filters import InputFilterAdmin


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

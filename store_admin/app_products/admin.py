from uuid import uuid4

from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from app_products.models import Product, Manufacturer, ProductFeature
from app_categories.admin import TypeFeatureFieldMixin
from app_products.filters import ProductCategoryFilter, ProductManufacturerFilter


class FeatureProductInline(TypeFeatureFieldMixin, admin.TabularInline):
    """Добавление характеристик для товаров"""
    model = ProductFeature
    fields = ['feature_fk', 'value', 'type_feature']
    readonly_fields = ['feature_fk', 'type_feature']

    def has_add_permission(self, request, obj) -> bool:
        """Возможность добавлять характеристики к товарам"""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Возможность удалять характеристики у товаров"""
        return False


class ListDisplayProductExtendMixin():
    """Миксин для расширения list_display"""
    list_select_related = ('category_fk', 'manufacturer_fk')
    list_display = ('name', 'price', 'added', 'category', 'manufacturer', 'is_limited')

    def get_queryset(self, request) -> QuerySet:
        queryset = super().get_queryset(request).select_related(*self.list_select_related)
        return queryset

    def category(self, obj) -> str:
        """Доп. поле отображения категория"""
        return obj.category_fk.name

    def manufacturer(self, obj) -> str:
        """Доп. поле отображения производитель"""
        return obj.manufacturer_fk.name

    category.short_description = _('category')
    manufacturer.short_description = _('manufacturer')


@admin.register(Product)
class ProductAdmin(ListDisplayProductExtendMixin, admin.ModelAdmin):
    """Панель продуктов"""
    inlines = (FeatureProductInline,)
    ordering = ('-added', )
    search_fields = ('name', )
    list_filter = (ProductCategoryFilter, ProductManufacturerFilter, 'is_limited')

    def save_model(self, request, obj, form, change) -> None:
        if not obj.product_id:
            obj.product_id = uuid4()

        if 'category_fk' in form.changed_data:
            obj.save(update_fields=form.changed_data)
        else:
            super().save_model(request, obj, form, change)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ('name',)

from uuid import uuid4

from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Feature, Product, Manufacturer, ProductFeature


class TypeFeatureFieldMixin():
    list_select_related = ('feature_fk',)

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request).select_related(*self.list_select_related)
    #     return queryset

    def type_feature(self, obj):
        return _(obj.feature_fk.get_type_feature_display())

    type_feature.short_description = _('type feature')


class FeatureProductInline(TypeFeatureFieldMixin, admin.TabularInline):
    # todo: можно создать свой формсет с разными виджатами
    model = ProductFeature
    fields = ['feature_fk', 'value', 'type_feature']
    readonly_fields = ['feature_fk', 'type_feature']

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """Панель характеристик"""
    list_display = ('name', 'type_feature')



class ListDisplayProductExtendMixin():
    list_select_related = ('category_fk', 'manufacturer_fk')
    list_display = ('name', 'price', 'added', 'category', 'manufacturer', 'is_limited')

    # def get_queryset(self, request):
    #     queryset = (
    #         super().get_queryset(request).prefetch_related(*self.list_prefetch_related)
    #     )
    #     return queryset

    def category(self, obj):
        """Доп. поле отображения категория"""
        return obj.category_fk

    def manufacturer(self, obj):
        """Доп. поле отображения производитель"""
        return obj.manufacturer_fk

    category.short_description = _('category')
    manufacturer.short_description = _('manufacturer')


@admin.register(Product)
class ProductAdmin(ListDisplayProductExtendMixin, admin.ModelAdmin):
    """Панель продуктов"""
    inlines = (FeatureProductInline,)
    ordering = ('-added', )
    # list_filter = ('name', 'is_limited', 'category_fk')
    # search_fields = ('name', 'category_fk', 'manufacturer_fk')
    list_filter = ('name', 'is_limited', 'category_fk__name', 'manufacturer_fk__name')
    search_fields = ('name', 'category_fk__name', 'manufacturer_fk__name')

    def save_model(self, request, obj, form, change):
        """
        Если не сохранена модель, то она сохраняется.
        Если есть, то сохраняется после inline элементов.
        """
        # сделано для невозможности сохранения лишних характеристик в продуктах
        if not obj.product_id:
            obj.product_id = uuid4()
            super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        formset.save()
        form.instance.save()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    pass

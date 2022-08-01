from uuid import uuid4

from django.contrib import admin
from django.utils.translation import gettext as _

from app_categories.models import Category, CategoryFeature


class TypeFeatureFieldMixin():
    list_select_related = ('feature_fk',)

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request).select_related(*self.list_select_related)
    #     return queryset

    def type_feature(self, obj):
        return _(obj.feature_fk.get_type_feature_display())

    type_feature.short_description = _('type feature')


class FeatureCategoryInline(TypeFeatureFieldMixin, admin.TabularInline):
    """Добавление характеристик для категории"""
    model = CategoryFeature
    fields = ['feature_fk', 'type_feature']
    extra = 2
    readonly_fields = ['type_feature']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Панель категорий"""
    list_display = ('name', 'is_active')
    inlines = (FeatureCategoryInline, )

    def save_model(self, request, obj, form, change):
        # todo: очень странно, но django не создает category_id с инлайном
        if not obj.category_id:
            obj.category_id = uuid4()
        return super().save_model(request, obj, form, change)

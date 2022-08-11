from uuid import uuid4
from mptt.admin import DraggableMPTTAdmin, MPTTModelAdmin

from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from app_categories.models import Category, CategoryFeature, Feature


class TypeFeatureFieldMixin():
    """Миксин для добавления поля и оптимизации запроса"""
    list_select_related = ('feature_fk', )

    def get_queryset(self, request) -> QuerySet:
        queryset = super().get_queryset(request).select_related(*self.list_select_related)
        return queryset

    @admin.display(description=_('type feature'))
    def type_feature(self, obj: CategoryFeature) -> str:
        """
        Поле типа характеристики.
        :param obj: запись в БД связи категории и характеристики,
        :return: значение поля в формате для пользователя
        """
        return _(obj.feature_fk.get_type_feature_display())


class FeatureCategoryInline(TypeFeatureFieldMixin, admin.TabularInline):
    """Добавление характеристик для категории"""
    model = CategoryFeature
    fields = ('feature_fk', 'type_feature')
    readonly_fields = ('type_feature',)

    def has_add_permission(self, request, obj) -> bool:
        """Если еще не создан объект нельзя добавлять характеристики"""
        if not obj or obj.is_root_node():
            return False
        return super().has_add_permission(request, obj)


class ActionsMixin():
    """Добавление груповых действий"""
    @admin.action(description=_('Mark is active'))
    def mark_is_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_('Mark is not active'))
    def mark_isnt_active(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin, ActionsMixin):
    """Панель категорий"""
    list_display = ('name', 'is_active')

    list_display_links = ('name',)
    mptt_indent_field = "name"
    mptt_level_indent = 40

    list_filter = ('is_active',)
    search_fields = ('name',)

    actions = [
        'mark_is_active',
        'mark_isnt_active'
    ]

    prepopulated_fields = {'slug': ('name',)}

    inlines = (FeatureCategoryInline, )
    #todo: здесь убрать изображение у категории-родителя

    def get_field_queryset(self, db, db_field, request) -> QuerySet:
        """Только 0 уровень вложенности"""
        queryset = super().get_field_queryset(db, db_field, request).filter(level=0)
        return queryset


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """Панель характеристик"""
    list_display = ('name', 'type_feature')
    list_filter = ('type_feature',)
    search_fields = ('name', )

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

    def type_feature(self, obj: CategoryFeature) -> str:
        """
        Поле типа характеристики.
        :param obj: запись в БД связи категории и характеристики,
        :return: значение поля в формате для пользователя
        """
        return _(obj.feature_fk.get_type_feature_display())

    type_feature.short_description = _('type feature')


class FeatureCategoryInline(TypeFeatureFieldMixin, admin.TabularInline):
    """Добавление характеристик для категории"""
    model = CategoryFeature
    fields = ('feature_fk', 'type_feature')
    extra = 1
    readonly_fields = ('type_feature',)

    def has_add_permission(self, request, obj) -> bool:
        """Если еще не создан объект нельзя добавлять характеристики"""
        if not obj:
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None) -> bool:
        """Если подкатегория нельзя удалять характеристики"""
        if obj and obj.is_child_node():
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None) -> bool:
        if obj and obj.level:
            return False
        return super().has_change_permission(request, obj)


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Панель категорий"""
    list_display = ('name', 'is_active')

    list_display_links = ('name',)
    mptt_indent_field = "name"
    mptt_level_indent = 40

    list_filter = ('is_active',)
    search_fields = ('name',)

    inlines = (FeatureCategoryInline, )

    def get_field_queryset(self, db, db_field, request) -> QuerySet:
        """Только 0 уровень вложенности"""
        queryset = super().get_field_queryset(db, db_field, request).filter(level=0)
        return queryset

    def save_model(self, request, obj, form, change) -> None:
        if not obj.category_id:
            obj.category_id = uuid4()
            super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change) -> None:
        """
        Изменение порядка сохранения.
        Если категория не меняется и это подкатегория, то нормальный порядок
        Если категория меняется и это родитель, то сначала изменение в характеристиках, потом в категориях
        """
        if form.changed_data or form.instance.is_root_node():
            formset.save()
            form.instance.save()
        else:
            form.instance.save()
            formset.save()


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """Панель характеристик"""
    list_display = ('name', 'type_feature')
    list_filter = ('type_feature',)
    search_fields = ('name', )

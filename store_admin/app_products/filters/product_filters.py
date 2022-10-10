from abc import ABC, abstractmethod
from typing import List
import django_filters


from django.db.models import QuerySet

from app_categories.models import Feature
from app_products.models import Product


class ProductFilterFeatureBase(ABC):
    def __init__(self, feature: Feature):
        self.feature = feature
        self.filter_obj = self.get_filter_obj()
        self.filter_obj.parent = self

    @abstractmethod
    def filter_method(self, queryset: QuerySet, name: None, value: str):
        pass


class FilterObjCharFilterMixin():
    """Миксин для создания поля Char фильтра """
    def get_filter_obj(self) -> django_filters.CharFilter:
        return django_filters.CharFilter(method='filter_method')


class FilterObjSelectFilterMixin():
    """Миксин для создания поля MultipleChoice фильтра """
    def get_filter_obj(self) -> django_filters.MultipleChoiceFilter:
        value_choices = (
            (product_feature.value, product_feature.value)
            for product_feature in self.feature.productfeature_set.all()
        )

        return django_filters.MultipleChoiceFilter(
            choices=value_choices, method='filter_method')


class ProductFilterFeatureText(ProductFilterFeatureBase,
                               FilterObjCharFilterMixin):
    """Фильтр для текстовых характеристик товаров"""
    def filter_method(self, queryset: QuerySet, name: None, value: str):
        """
        Фильтрация по текущей характеристики (ICONSTAINS)
        :param queryset: Queryset из view
        :param name: None
        :param value: значение, введеное в поле
        :return: отфильтрованный Queryset
        """
        queryset = queryset.filter(
            productfeature__feature_fk=self.feature.feature_id,
            productfeature__value__icontains=value
        )
        return queryset


class ProductFilterFeatureCheckbox(ProductFilterFeatureBase,
                                   FilterObjCharFilterMixin):
    """Фильтр для характеристик товаров типа да/нет"""
    def filter_method(self, queryset: QuerySet, name: None, value: str):
        """
        Фильтрация по текущей характеристики (да/нет)
        :param queryset: Queryset из view
        :param name: None
        :param value: 'on' если флаг нажат
        :return: отфильтрованный Queryset
        """
        if value == 'on':
            queryset = queryset.filter(
                productfeature__feature_fk=self.feature.feature_id,
                productfeature__value__contains='yes')
        return queryset


class ProductFilterFeatureSelect(ProductFilterFeatureBase,
                                 FilterObjSelectFilterMixin):
    """Фильтр для характеристик товаров типа MultiChoice"""
    def filter_method(self, queryset: QuerySet, name: None, value: List[str]):
        """
        Фильтрация по текущей характеристики (select)
        :param queryset: Queryset из view
        :param name: None
        :param value: список выбранный значений
        :return: отфильтрованный Queryset
        """
        queryset = queryset.filter(
            productfeature__feature_fk=self.feature.feature_id,
            productfeature__value__in=value
        )
        return queryset


class FactoryFilterFeature():
    """Фабрика фильтров """
    _FILTER_FEATURE = {
        'select': ProductFilterFeatureSelect,
        'checkbox': ProductFilterFeatureCheckbox,
        'text': ProductFilterFeatureText
    }

    def get_filter_class(self, feature: Feature):
        """
        Возвращает класс фильтра для характеристики в зависимости от типа.
        :param feature: текущая характеристика,
        :return: класс фильтра
        """
        return self._FILTER_FEATURE.get(feature.type_feature)


class ProductFilterCommon(django_filters.FilterSet):
    """Общий для всех категорий фильтр. Цена, Наименование и Наличие"""
    price = django_filters.CharFilter(field_name='price',
                                      method='filter_price')
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')
    available = django_filters.CharFilter(field_name='count',
                                          method='filter_available')
    manufacturer = django_filters.CharFilter(
        field_name='manufacturer_fk__name', lookup_expr='icontains')

    def filter_price(self, queryset: QuerySet, name: str, value: str):
        """
        Фильтрация по цене
        :param queryset: Queryset из view
        :param name: имя поля в модели Product
        :param value: значение по которому фильтровать вида '0;203'
        :return: отфильтрованный Queryset
        """
        value = [float(price) for price in value.split(';')]
        name = f'{name}__range'
        queryset = queryset.filter(**{name: value})
        return queryset

    def filter_available(self, queryset, name, value):
        """
        Фильтрация по наличию
        :param queryset: Queryset из view
        :param name: имя поля в модели Product
        :param value: 'on' если флаг нажат
        :return: отфильтрованный Queryset
        """
        if value == 'on':
            name = f'{name}__gt'
            queryset = queryset.filter(**{name: 0})
        return queryset


class ProductFilter(ProductFilterCommon):
    """Объект фильтра для товаров. Внешний интерфейс"""
    def __init__(self, *args, **kwargs):
        features = kwargs.pop('features')
        super(ProductFilter, self).__init__(*args, **kwargs)
        self.add_filters(features)

    def add_filters(self, features: QuerySet) -> None:
        """
        Добавление фильтров для характеристик в зависимости от категории.
        :param features: queryset с характеристиками для текущей категории.
        """
        filter_factory = FactoryFilterFeature()

        for feature in features:
            filter_class = filter_factory.get_filter_class(feature)
            if filter_class:
                self.filters.update({
                    str(feature.slug):
                        filter_class(feature).filter_obj
                })

            self.Meta.fields.append(str(feature.feature_id))

    class Meta:
        model = Product
        fields = ['price', 'name', 'available', 'manufacturer']

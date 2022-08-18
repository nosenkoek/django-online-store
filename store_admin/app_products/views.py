from typing import List

from django.db.models import Max, Prefetch
from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from app_categories.views import NaviCategoriesList
from app_categories.models import Category, Feature
from app_products.filters import ProductFilter
from app_products.forms import FilterProductForm
from app_products.models import Product, ProductFeature
from app_products.services import SortedItem


class AddSortedItemToContextMixin():
    """Миксин для добавления полей сортировки товаров"""
    SORTED_LIST = [
        SortedItem('price', 'Цене'),
        SortedItem('added', 'Новизне')
    ]

    def add_sorted_item_to_context(self) -> None:
        """ Добавление списка полей для сортировки"""
        self.extra_context.update({'sorted_list': self.SORTED_LIST})


class FilterFormMixin(FormMixin):
    #todo: удалить, если не нужно будет
    """Миксин для создания формы фильтра"""
    form_class = FilterProductForm

    def get_form_kwargs(self):
        kwargs = super(FilterFormMixin, self).get_form_kwargs()
        kwargs.update({'features': self.features})
        return kwargs


class ProductList(ListView, AddSortedItemToContextMixin):
    model = Product
    template_name = 'app_product/list_products.html'
    context_object_name = 'products'
    paginate_by = 8
    extra_context = NaviCategoriesList().get_context()
    subcategory, features = None, None

    # todo: подумать, этот метод добавляет +4 запроса к БД
    # @property
    # def subcategory(self) -> Category:
    #     subcategory_slug = self.kwargs.get('subcategory_slug')
    #     subcategory = Category.objects.filter(slug=subcategory_slug) \
    #         .select_related('parent') \
    #         .prefetch_related('features') \
    #         .annotate(max_price=Max('product__price')) \
    #         .first()
    #     return subcategory
    #
    # @property
    # def features(self):
    #     subcategory_slug = self.kwargs.get('subcategory_slug')
    #     features = Feature.objects.filter(categories__slug=subcategory_slug) \
    #         .prefetch_related(
    #         Prefetch('productfeature_set',
    #                  queryset=ProductFeature.objects
    #                  .filter(feature_fk__type_feature='select')
    #                  .distinct('value')))
    #     return features

    def add_filter(self) -> None:
        """Добавляет queryset для создания блока фильтра"""
        subcategory_slug = self.kwargs.get('subcategory_slug')
        self.subcategory = Category.objects.filter(slug=subcategory_slug) \
            .select_related('parent') \
            .prefetch_related('features') \
            .annotate(max_price=Max('product__price')) \
            .first()

        self.features = Feature.objects \
            .filter(categories=self.subcategory) \
            .prefetch_related(Prefetch('productfeature_set',
                                       queryset=ProductFeature.objects
                                       .filter(
                                           feature_fk__type_feature='select')
                                       .distinct('value')))

        self.extra_context.update({'subcategory': self.subcategory,
                                   'features': self.features})

    def get_queryset(self) -> None:
        self.add_sorted_item_to_context()
        self.add_filter()

        queryset = Product.objects.filter(category_fk=self.subcategory)

        if not self.request.GET.get('sort'):
            queryset = queryset.order_by('?')
        else:
            ordering = self.request.GET.get('sort')
            queryset = queryset.order_by(ordering)

        return ProductFilter(self.request.GET, queryset=queryset).qs



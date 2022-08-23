from typing import Tuple

from django.db.models import Max, Prefetch, QuerySet
from django.views.generic import ListView, DetailView

from app_categories.views import NaviCategoriesList
from app_categories.models import Category, Feature
from app_products.filters import ProductFilter
from app_products.models import Product, ProductFeature
from app_products.services import SortedItem, InitialDictFromURLMixin


class AddSortedItemToContextMixin():
    """Миксин для добавления полей сортировки товаров"""
    SORTED_LIST = [
        SortedItem('price', 'Цене'),
        SortedItem('added', 'Новизне')
    ]

    def add_sorted_item_to_context(self) -> None:
        """ Добавление списка полей для сортировки"""
        self.extra_context.update({'sorted_list': self.SORTED_LIST})


class ProductListView(ListView, AddSortedItemToContextMixin,
                      InitialDictFromURLMixin):
    model = Product
    template_name = 'app_products/product_list.html'
    context_object_name = 'products'
    paginate_by = 8
    extra_context = NaviCategoriesList().get_context()

    def get_subcategory_and_features(self) -> Tuple[Category, QuerySet]:
        """Возвращает объект категории и его характеристики"""
        subcategory_slug = self.kwargs.get('subcategory_slug')
        subcategory = Category.objects.filter(slug=subcategory_slug) \
            .select_related('parent') \
            .prefetch_related('features') \
            .annotate(max_price=Max('product__price')) \
            .first()

        features = Feature.objects \
            .filter(categories=subcategory) \
            .prefetch_related(Prefetch('productfeature_set',
                                       queryset=ProductFeature.objects
                                       .filter(
                                           feature_fk__type_feature='select')
                                       .distinct('value')))
        return subcategory, features

    def get_queryset(self) -> QuerySet:
        self.add_sorted_item_to_context()
        subcategory, features = self.get_subcategory_and_features()

        queryset = Product.objects.filter(category_fk=subcategory)

        if not self.request.GET.get('sort'):
            queryset = queryset.order_by('?')
        else:
            ordering = self.request.GET.get('sort')
            queryset = queryset.order_by(ordering)

        product_filter = ProductFilter(self.request.GET,
                                       queryset=queryset,
                                       features=features)
        self.extra_context.update({
            'subcategory': subcategory,
            'features': features,
            'form': product_filter.form,
        })
        return product_filter.qs

    def get_context_data(self, **kwargs) -> dict:
        context = super(ProductListView, self).get_context_data(**kwargs)
        initial_dict = self.get_initial_dict()
        context.update({'initial_dict': initial_dict})
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'app_products/product_detail.html'
    extra_context = NaviCategoriesList().get_context()

    def get_context_data(self, **kwargs) -> dict:
        context_data = super(ProductDetailView, self).get_context_data(
            **kwargs)
        product = self.get_object()
        subcategory = Category.objects.filter(product=product) \
            .select_related('parent').first()
        context_data.update({'subcategory': subcategory})
        return context_data

    def get_queryset(self) -> QuerySet:
        queryset = super(ProductDetailView, self).get_queryset() \
            .prefetch_related('productfeature_set',
                              'productfeature_set__feature_fk')
        return queryset

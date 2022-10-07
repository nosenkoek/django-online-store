import logging
from typing import Tuple

from django.db.models import Max, Prefetch, QuerySet
from django.views.generic import ListView, DetailView
from redis.exceptions import RedisError

from app_categories.services.navi_categories_list import \
    NaviCategoriesList
from app_categories.models import Category, Feature
from app_products.filters import ProductFilter
from app_products.models import Product, ProductFeature
from app_products.services.decorator_count_views import \
    cache_popular_product, NAME_ATRS_CACHE
from app_products.services.handler_url_params import InitialDictFromURLMixin
from app_products.services.sorted_item import AddSortedItemToContextMixin
from utils.context_managers import redis_connection

logger = logging.getLogger(__name__)


class ProductListView(ListView, AddSortedItemToContextMixin,
                      InitialDictFromURLMixin):
    """View для каталога товаров"""
    model = Product
    template_name = 'app_products/product_list.html'
    context_object_name = 'products'
    paginate_by = 8

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
        context.update(NaviCategoriesList().get_context())
        return context


class ProductDetailView(DetailView):
    """View для детальной страницы товара"""
    model = Product
    template_name = 'app_products/product_detail.html'

    def get_queryset(self) -> QuerySet:
        queryset = super(ProductDetailView, self).get_queryset() \
            .select_related('category_fk', 'category_fk__parent',
                            'manufacturer_fk') \
            .prefetch_related('productfeature_set',
                              'productfeature_set__feature_fk')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        return context

    @cache_popular_product
    def get(self, request, *args, **kwargs):
        return super(ProductDetailView, self).get(request, *args, **kwargs)


class PopularProductListView(ListView):
    """View для страницы популярных товаров"""
    model = Product
    context_object_name = 'popular_products'
    template_name = 'app_products/popular_product_list.html'

    def get_queryset(self) -> QuerySet:
        try:
            with redis_connection() as redis_conn:
                popular_product_range = redis_conn.lrange(
                    NAME_ATRS_CACHE.get(self.request.get_host())[1], 0, -1
                )
        except RedisError as err:
            logger.error(f'Error connection to Redis | {err}')
            logger.warning('not cache popular product')
            popular_product_range = []

        queryset = super(PopularProductListView, self).get_queryset() \
            .select_related('category_fk', 'category_fk__parent') \
            .filter(category_fk__is_active=True,
                    product_id__in=popular_product_range)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PopularProductListView, self)\
            .get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        return context

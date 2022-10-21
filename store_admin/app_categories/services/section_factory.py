from abc import ABC

from django.views.generic import ListView
from django.db.models import Min, QuerySet

from app_categories.models import Category
from app_products.models import Product


class BaseFactory(ABC, ListView):
    """Базовый класс секций на главной страницы"""

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """Переопределение метода для получения в потомках context_data"""
        object_list = self.get_queryset()
        return super(BaseFactory, self) \
            .get_context_data(object_list=object_list, **kwargs)


class RandomCategoriesList(BaseFactory):
    """Описание секции случайных категорий"""
    model = Category
    queryset = Category.objects.filter(is_active=True, level=1) \
        .select_related('parent') \
        .annotate(min_price=Min('product__price')) \
        .order_by('?')[:3]
    context_object_name = 'random_categories'


class PopularProductsList(BaseFactory):
    """Описание секции популярных товаров"""
    model = Product
    queryset = Product.objects.select_related('category_fk',
                                              'category_fk__parent')
    context_object_name = 'popular_products'

    def get_queryset(self) -> QuerySet:
        queryset = super(PopularProductsList, self).get_queryset()

        queryset = queryset.filter(category_fk__is_active=True,
                                   product_id__in=self.popular_product_range)
        return queryset


class LimitEditionList(BaseFactory):
    """Описание секции лимитированных товаров"""
    model = Product
    queryset = Product.objects.filter(is_limited=True) \
        .order_by('-added') \
        .select_related('category_fk', 'category_fk__parent') \
        .filter(category_fk__is_active=True)[:16]
    context_object_name = 'limit_edition'


class SectionsFactory():
    """Фабрика view для секций """
    SECTIONS = {
        'random_categories': RandomCategoriesList(),
        'popular_products': PopularProductsList(),
        'limit_edition': LimitEditionList()
    }

    def get_section_view(self, context_name: str) -> BaseFactory:
        """
        Возвращает объект view секции
        :param context_name: название секции
        :return: объект view секции
        """
        return self.SECTIONS.get(context_name)

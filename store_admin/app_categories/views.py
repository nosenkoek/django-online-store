from abc import ABC

from django.db.models import Min, QuerySet
from django.views.generic import ListView, TemplateView

from app_categories.models import Category
from app_products.models import Product
from app_products.services.decorator_count_views import redis_conn, \
    NAME_ATRS_CACHE


class NaviCategoriesList(ListView):
    """Класс навигации в хедере"""
    model = Category
    queryset = Category.objects.filter(is_active=True, level=0) \
        .prefetch_related('children')
    context_object_name = 'navi_categories'

    def get_context(self):
        return {self.context_object_name: self.get_queryset()}


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
        .order_by('?') \
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


class MainPageView(TemplateView):
    """View для главной страницы"""
    template_name = 'app_categories/main_page.html'
    extra_context = NaviCategoriesList().get_context()

    def get_context_data(self, **kwargs):
        context_data = super(MainPageView, self).get_context_data(**kwargs)
        sections = SectionsFactory()

        sections.SECTIONS['popular_products'].popular_product_range = \
            redis_conn.lrange(NAME_ATRS_CACHE.get(self.request.get_host())[1],
                              0, 7)

        for _, item in sections.SECTIONS.items():
            context_data.update(item.get_context_data())
        return context_data


class SubcategoriesListView(ListView):
    """View для списка подкатегорий"""
    model = Category
    template_name = 'app_categories/subcategory_list.html'
    context_object_name = 'subcategories'
    extra_context = NaviCategoriesList().get_context()

    def get_queryset(self) -> QuerySet:
        category_slug = self.kwargs.get('category_slug')

        queryset = Category.objects.filter(parent__slug=category_slug) \
            .select_related('parent') \
            .annotate(min_price=Min('product__price'))

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        context_data = super(SubcategoriesListView, self).get_context_data()
        context_data.update({
            'category': Category.objects.get(
                slug=self.kwargs.get('category_slug')
            )
        })
        return context_data

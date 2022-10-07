import logging

from django.db.models import Min, QuerySet
from django.views.generic import ListView, TemplateView
from redis.exceptions import RedisError

from app_categories.models import Category
from app_categories.services.section_factory import SectionsFactory
from app_products.services.decorator_count_views import NAME_ATRS_CACHE
from utils.context_managers import redis_connection
from app_categories.services.navi_categories_list import \
    NaviCategoriesList

logger = logging.getLogger(__name__)


class MainPageView(TemplateView):
    """View для главной страницы"""
    template_name = 'app_categories/main_page.html'

    def get_context_data(self, **kwargs):
        context_data = super(MainPageView, self).get_context_data(**kwargs)
        sections = SectionsFactory()

        try:
            with redis_connection() as redis_conn:
                sections.SECTIONS['popular_products'].popular_product_range = \
                    redis_conn.lrange(
                        NAME_ATRS_CACHE.get(self.request.get_host())[1],
                        0, 7)
        except RedisError as err:
            logger.error(f'Error connection to Redis | {err}')
            logger.warning('not cache popular product')
            sections.SECTIONS['popular_products'].popular_product_range = []

        for _, item in sections.SECTIONS.items():
            context_data.update(item.get_context_data())

        context_data.update(NaviCategoriesList().get_context())
        return context_data


class SubcategoriesListView(ListView):
    """View для списка подкатегорий"""
    model = Category
    template_name = 'app_categories/subcategory_list.html'
    context_object_name = 'subcategories'

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
        context_data.update(NaviCategoriesList().get_context())
        return context_data

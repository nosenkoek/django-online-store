from typing import Dict

from django.core.cache import cache
from django.db.models import QuerySet
from django.views.generic import ListView

from app_categories.models import Category


class NaviCategoriesList(ListView):
    """Класс навигации в хедере"""
    model = Category
    queryset = Category.objects.filter(is_active=True, level=0) \
        .prefetch_related('children')
    context_object_name = 'navi_categories'

    def get_context(self) -> Dict[str, QuerySet]:
        """Формирует данные для добавления в контекст меню категорий"""
        navi_cache_key = f'navi_{self.context_object_name}'
        queryset = cache.get_or_set(navi_cache_key, self.get_queryset(), 60)
        return {self.context_object_name: queryset}

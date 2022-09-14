from django.views.generic import ListView

from app_categories.models import Category


class NaviCategoriesList(ListView):
    """Класс навигации в хедере"""
    model = Category
    queryset = Category.objects.filter(is_active=True, level=0) \
        .prefetch_related('children')
    context_object_name = 'navi_categories'

    def get_context(self):
        return {self.context_object_name: self.get_queryset()}

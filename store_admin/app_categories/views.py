from django.db.models import Min
from django.shortcuts import render
from django.views.generic import ListView
from django.views import View

from app_categories.models import Category


class SubcategoriesList(View):
    def get(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug')
        categories = Category.objects.filter(is_active=True, level=0)
        subcategories = Category.objects.filter(parent__slug=category_slug).annotate(min_price=Min('product__price'))

        context_data = {
            'title': 'title',
            'categories': categories,
            'subcategories': subcategories
        }
        return render(request, 'app_categories/list_subcategories.html', context_data)

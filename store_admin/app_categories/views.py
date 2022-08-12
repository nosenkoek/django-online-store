from django.db.models import Min, QuerySet
from django.shortcuts import render
from django.views.generic import ListView
from django.views import View

from app_categories.models import Category
from app_products.models import Product


class NaviCategoriesMixin():
    # todo: апдейтить контекст дату надо!!
    def get_queryset_categories(self) -> QuerySet:
        categories = Category.objects.filter(is_active=True, level=0)\
                                    .prefetch_related('children')
        return categories


class MainPageView(View, NaviCategoriesMixin):
    def get(self, request):
        categories = self.get_queryset_categories()
        random_categories = Category.objects.filter(is_active=True, level=1) \
                                    .select_related('parent') \
                                    .annotate(min_price=Min('product__price')) \
                                    .order_by('?')[:3]
        popular_products = Product.objects.order_by('?')\
                                    .select_related('category_fk', 'category_fk__parent')\
                                    .filter(category_fk__is_active=True)[:8]
        limit_edition = Product.objects.filter(is_limited=True) \
                                .order_by('?') \
                                .select_related('category_fk', 'category_fk__parent')\
                                .filter(category_fk__is_active=True)[:16]

        context_data = {
            'categories': categories,
            'random_categories': random_categories,
            'popular_products': popular_products,
            'limit_edition': limit_edition
        }

        return render(request, 'app_categories/main_page.html', context=context_data)


class SubcategoriesList(View, NaviCategoriesMixin):
    def get(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug')
        categories = categories = self.get_queryset_categories()
        subcategories = Category.objects.filter(parent__slug=category_slug)\
                                        .select_related('parent')\
                                        .annotate(min_price=Min('product__price'))
        category = Category.objects.get(slug=category_slug)

        context_data = {
            'title': 'title',
            'categories': categories,
            'subcategories': subcategories,
            'category': category
        }
        return render(request, 'app_categories/list_subcategories.html', context_data)

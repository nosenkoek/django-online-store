from typing import List

from django.views.generic import ListView

from app_categories.views import NaviCategoriesList
from app_categories.models import Category
from app_products.models import Product
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


class ProductList(ListView, AddSortedItemToContextMixin):
    model = Product
    template_name = 'app_product/list_products.html'
    context_object_name = 'products'
    paginate_by = 8
    extra_context = NaviCategoriesList().get_context()

    def get_queryset(self):
        subcategory_slug = self.kwargs.get('subcategory_slug')
        subcategory = Category.objects.filter(
            slug=subcategory_slug).select_related('parent').first()

        self.extra_context.update({'subcategory': subcategory})

        queryset = Product.objects.filter(category_fk=subcategory)
        self.add_sorted_item_to_context()

        if not self.request.GET.get('sort'):
            queryset = queryset.order_by('?')
        else:
            ordering = self.request.GET.get('sort')
            queryset = queryset.order_by(ordering)
        return queryset

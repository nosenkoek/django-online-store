from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from app_categories.views import NaviCategoriesMixin
from app_categories.models import Category
from app_products.models import Product


class ProductList(ListView, NaviCategoriesMixin):
    model = Product
    template_name = 'app_product/list_products.html'
    context_object_name = 'products'
    paginate_by = 8

    def get(self, request, *args, **kwargs):
        # category_slug = kwargs.get('category_slug')
        subcategory_slug = kwargs.get('subcategory_slug')
        subcategory = Category.objects.filter(slug=subcategory_slug).select_related('parent').first()
        self.queryset = Product.objects.filter(category_fk=subcategory).order_by('-added')

        self.extra_context = {
            'categories': self.get_queryset_categories(),
            'subcategory': subcategory,
        }

        return super().get(request, *args, **kwargs)


# class ProductList(View, NaviCategoriesMixin):
#     def get(self, request, *args, **kwargs):
#         category_slug = kwargs.get('category_slug')
#         subcategory_slug = kwargs.get('subcategory_slug')
#         subcategory = Category.objects.filter(slug=subcategory_slug).select_related('parent').first()
#
#         context_data = {
#             'categories': self.get_queryset_categories(),
#             'subcategory': subcategory,
#         }
#         print(kwargs)
#         return render(request, 'app_product/list_products.html', context_data)

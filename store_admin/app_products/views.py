from django.views.generic import ListView

from app_categories.views import NaviCategoriesList
from app_categories.models import Category
from app_products.models import Product


class ProductList(ListView):
    model = Product
    template_name = 'app_product/list_products.html'
    context_object_name = 'products'
    paginate_by = 8
    extra_context = NaviCategoriesList().get_context_data()

    def get_queryset(self):
        subcategory_slug = self.kwargs.get('subcategory_slug')
        subcategory = Category.objects.filter(
            slug=subcategory_slug).select_related('parent').first()
        queryset = Product.objects.filter(category_fk=subcategory)\
            .order_by('-added')

        self.extra_context = {'subcategory': subcategory}
        return queryset

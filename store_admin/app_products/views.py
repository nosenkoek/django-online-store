from django.shortcuts import render
from django.views import View
from django.db.models import Min

from app_categories.models import Category
from app_products.models import Product


class MainPageView(View):
    def get(self, request):
        # todo: подумать как привязать к запросу подкатегории select_related
        categories = Category.objects.filter(is_active=True, level=0)

        random_categories = Category.objects.filter(is_active=True, level=1) \
                                    .annotate(min_price=Min('product__price')) \
                                    .order_by('?') \
                                    .only('name', 'icon')[:3]
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

        return render(request, 'app_product/main_page.html', context=context_data)



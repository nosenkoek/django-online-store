from django.db.models import QuerySet, Max
from django.views.generic import ListView

from app_categories.services.navi_categories_list import \
    NaviCategoriesList
from app_products.models import Product
from app_products.services.sorted_item import AddSortedItemToContextMixin
from app_products.filters import ProductFilterCommon
from app_products.services.handler_url_params import InitialDictFromURLMixin
from app_search.services.search_result_mixin import SearchResultMixin


class SearchResultListView(ListView, AddSortedItemToContextMixin,
                           InitialDictFromURLMixin, SearchResultMixin):
    model = Product
    context_object_name = 'products'
    paginate_by = 8
    template_name = 'app_search/search_list.html'
    extra_context = NaviCategoriesList().get_context()

    def get_queryset(self) -> QuerySet:
        self.add_sorted_item_to_context()
        query = self.request.GET.get('query')
        product_ids = self.search_match(query)

        queryset = Product.objects.filter(product_id__in=product_ids)\
            .select_related('manufacturer_fk', 'category_fk',
                            'category_fk__parent')
        price_max = queryset.aggregate(price_max=Max('price')).get('price_max')

        if not self.request.GET.get('sort'):
            queryset = queryset.order_by('?')
        else:
            ordering = self.request.GET.get('sort')
            queryset = queryset.order_by(ordering)

        product_filter = ProductFilterCommon(self.request.GET,
                                             queryset=queryset)
        self.extra_context.update({
            'form': product_filter.form,
            'price_max': price_max
        })
        return product_filter.qs

    def get_context_data(self, **kwargs) -> dict:
        context = super(SearchResultListView, self).get_context_data(**kwargs)
        initial_dict = self.get_initial_dict()
        context.update({'initial_dict': initial_dict})
        return context

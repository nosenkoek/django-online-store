from django.urls import path

from app_products.views import ProductListView, ProductDetailView

urlpatterns = [
    path('<slug:category_slug>/<slug:subcategory_slug>/',
         ProductListView.as_view(),
         name='product_list'),
    path('<slug:slug>/', ProductDetailView.as_view(),
         name='product_detail')
]

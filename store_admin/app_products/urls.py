from django.urls import path

from app_products.views import ProductList

urlpatterns = [
    path('<slug:category_slug>/<slug:subcategory_slug>/',
         ProductList.as_view(),
         name='list_products'),
]

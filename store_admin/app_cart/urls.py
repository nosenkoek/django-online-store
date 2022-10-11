from django.urls import path

from app_cart.views import CartView, AddProductCartView, \
    DeleteProductCartView, ClearCartView

urlpatterns = [
    path('view/', CartView.as_view(), name='cart'),
    path('product_add/<uuid:product_id>', AddProductCartView.as_view(),
         name='cart_add_product'),
    path('product_delete/<uuid:product_id>', DeleteProductCartView.as_view(),
         name='cart_delete_product'),
    path('clear', ClearCartView.as_view(),
         name='cart_clear'),
]

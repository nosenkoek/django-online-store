from django.urls import path

from app_cart.views import CartView, AddProductCartView, \
    DeleteAllProductCartView, ClearCartView, UpdateProductCartVIew, \
    RemoveProductCartView

urlpatterns = [
    path('view/', CartView.as_view(), name='cart'),
    path('product_add/<uuid:product_id>', AddProductCartView.as_view(),
         name='cart_add_product'),
    path('product_update/<uuid:product_id>', UpdateProductCartVIew.as_view(),
         name='cart_update_product'),
    path('product_remove/<uuid:product_id>', RemoveProductCartView.as_view(),
         name='cart_remove_product'),
    path('product_delete/<uuid:product_id>',
         DeleteAllProductCartView.as_view(),
         name='cart_delete_product'),
    path('clear', ClearCartView.as_view(),
         name='cart_clear'),
]

from django.urls import path

from app_order.views import CheckoutView

urlpatterns = [
    path('checkout/', CheckoutView.as_view(),
         name='order'),
]

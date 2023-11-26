from django.urls import path

from app_order.views import CheckoutView, OrderHistoryListView, OrderDetailView

urlpatterns = [
    path('<int:number>/', OrderDetailView.as_view(), name='order_detail'),
    path('checkout/', CheckoutView.as_view(),  name='order'),
    path('history/', OrderHistoryListView.as_view(), name='order_history'),

]

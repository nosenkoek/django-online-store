from django.urls import path

from app_payment.views import PaymentProgressView, PaymentView

urlpatterns = [
    path('pay/<str:order_id>', PaymentView.as_view(), name='pay'),
    path('progress/<str:order_id>', PaymentProgressView.as_view(),
         name='payment_progress'),
]

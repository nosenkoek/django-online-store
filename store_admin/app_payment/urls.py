from django.urls import path

from app_payment.views import PayView, PaymentCardView, PaymentProgressView, \
    PaymentAccountView

urlpatterns = [
    path('pay/<str:order_id>', PayView.as_view(), name='pay'),
    path('card/<str:order_id>', PaymentCardView.as_view(),
         name='payment_card'),
    path('account//<str:order_id>', PaymentAccountView.as_view(),
         name='payment_account'),
    path('progress/', PaymentProgressView.as_view(), name='payment_progress'),
]

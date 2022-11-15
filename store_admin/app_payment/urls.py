from django.urls import path

from app_payment.views import PaymentCard, PaymentProgress, PaymentAccount

urlpatterns = [
    path('card/', PaymentCard.as_view(), name='payment_card'),
    path('account/', PaymentAccount.as_view(), name='payment_account'),
    path('progress/', PaymentProgress.as_view(), name='payment_progress'),
]

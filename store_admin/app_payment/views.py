from django.views.generic import TemplateView


class PaymentProgress(TemplateView):
    template_name = 'app_payment/payment_progress.html'


class PaymentCard(TemplateView):
    template_name = 'app_payment/payment_card.html'


class PaymentAccount(TemplateView):
    template_name = 'app_payment/payment_account.html'

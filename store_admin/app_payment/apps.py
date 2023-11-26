from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppPaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_payment'
    verbose_name = _('payments')

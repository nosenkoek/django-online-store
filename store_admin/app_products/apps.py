from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_products'
    verbose_name = _('products')

    def ready(self):
        pass

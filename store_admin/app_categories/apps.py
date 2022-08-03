from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.core.signals import request_finished


class AppCategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_categories'
    verbose_name = _('categories')

    def ready(self):
        from app_categories.signals import add_features_subcategory
        pass

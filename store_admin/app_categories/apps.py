from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppCategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_categories'
    verbose_name = _('categories')

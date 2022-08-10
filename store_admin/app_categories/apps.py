from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import m2m_changed


class AppCategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_categories'
    verbose_name = _('categories')

    # def ready(self):
    #     from app_categories import signals

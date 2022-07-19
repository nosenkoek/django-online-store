from django.contrib import admin

from store.models import Feature


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    pass

from django.urls import path

from app_categories.views import SubcategoriesList


urlpatterns = [
    path('<slug:category_slug>/', SubcategoriesList.as_view(), name='subcategories')
]


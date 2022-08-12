from django.urls import path

from app_categories.views import MainPageView, SubcategoriesList


urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
    path('<slug:category_slug>/', SubcategoriesList.as_view(), name='subcategories')
]


from django.urls import path

from app_categories.views import MainPageView, SubcategoriesListView


urlpatterns = [
    path('',
         MainPageView.as_view(),
         name='main_page'),

    path('<slug:category_slug>/',
         SubcategoriesListView.as_view(),
         name='subcategory_list')
]

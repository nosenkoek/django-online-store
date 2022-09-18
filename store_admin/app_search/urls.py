from django.urls import path

from app_search.views import SearchResultListView


urlpatterns = [
    path('',
         SearchResultListView.as_view(),
         name='search_list'),
]

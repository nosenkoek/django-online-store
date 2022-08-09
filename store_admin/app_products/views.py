from django.shortcuts import render
from django.views import View

from app_categories.models import Category


class MainPageView(View):
    def get(self, request):
        categories = Category.objects.filter(is_active=True, level=0).all()
        return render(request, 'app_product/main_page.html', {'categories': categories})


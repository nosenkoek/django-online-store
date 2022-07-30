from django.shortcuts import render
from django.views import View

from .models import Category


class MainPageView(View):
    def get(self, request):
        categories = Category.objects.filter(is_active=True).all()

        return render(request, 'store/main_page.html', {'categories': categories})


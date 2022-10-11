from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.i18n import JavaScriptCatalog

urlpatterns = i18n_patterns(
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('search/', include('app_search.urls')),
    path('', include('app_categories.urls')),
    path('catalog/', include('app_products.urls')),
    path('users/', include('app_users.urls')),
    path('cart/', include('app_cart.urls'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

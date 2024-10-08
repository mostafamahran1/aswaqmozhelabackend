from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import search_all_products

urlpatterns = [
    path('search/', search_all_products, name='search_all_products'),
    # other URL patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

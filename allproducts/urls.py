from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import search_all_products , GetModelNames ,  get_latest_products , get_product_by_model_and_id

urlpatterns = [
    path('search/', search_all_products, name='search_all_products'),
    path('model-names/', GetModelNames.as_view(), name='get_model_names'),
    path('latest-products/', get_latest_products, name='get_latest_products'),
    path('product/', get_product_by_model_and_id, name='get_product_by_model_and_id'),
    # other URL patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/allproducts/', include('allproducts.urls')),
    path('', include('offerspaner.urls')),
    path('api/', include('products.urls')),
    path('api/toys/', include('toys.urls')),
    path('api/phones/', include('phones.urls')),
    path('api/clothes/', include('clothes.urls')),
    path('api/foods/', include('foods.urls')),
    path('api/fruitsandvedetables/', include('fruitsandvegetables.urls')),
    path('api/pharmacy/', include('pharmacy.urls')),
    path('api/spices/', include('spices.urls')),
    path('api/supermarket/', include('supermarket.urls')),
    path('api/', include('account.urls')),
    path('api/', include('order.urls')),
    path('api/token/', TokenObtainPairView.as_view()),
]

# تضمين مسارات الوسائط إذا كانت DEBUG مفعلة
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



handler404 = 'utils.error_view.handler404'
handler500 = 'utils.error_view.handler500'
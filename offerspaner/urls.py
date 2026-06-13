from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, TopBannerViewSet # استيراد الـ ViewSet الجديد
from . import views

router = DefaultRouter()
router.register(r'images', ImageViewSet)

# راوتر مستقل تماماً للبانر العلوي الجديد
top_banner_router = DefaultRouter()
top_banner_router.register(r'images', TopBannerViewSet)

urlpatterns = [
    path('api/offerspaner/', include(router.urls)),      # الـ API القديم الخاص بالأنيميشن الأصلي (دون تغيير)
    path('api/topbanner/', include(top_banner_router.urls)), # الـ API الجديد الخاص بالبانر العلوي الجديد 🚀
    path('', views.home, name='home'),
]
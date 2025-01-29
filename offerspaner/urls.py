from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet
from . import views

router = DefaultRouter()
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('api/offerspaner/', include(router.urls)),
    path('', views.home, name='home'),
]

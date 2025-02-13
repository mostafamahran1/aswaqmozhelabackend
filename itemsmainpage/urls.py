from django.urls import path
from .views import category_list, category_detail

urlpatterns = [
    path('api/itemsmainpage/', category_list, name='category-list'),  # كل الفئات
    path('api/itemsmainpage/<int:category_id>/', category_detail, name='category-detail'),  # فئة معينة
]

from django.urls import path
from . import addresses, views

urlpatterns = [
    path('addresses/', addresses.addresses, name='saved_addresses'),
    path('addresses/<int:pk>/', addresses.address_detail, name='saved_address_detail'),
    path('orders/', views.get_all_orders,name='get_orders'),
    path('user-orders/', views.get_user_orders, name='get_user_orders'),
    path('orders/new/', views.new_order,name='new_order'),
    path('orders/welcome-offer/', views.welcome_offer, name='welcome_offer'),
    path('orders/<str:pk>/', views.get_order,name='get_order'),
    path('orders/<str:pk>/process/', views.process_order,name='process_order'),
    path('orders/<str:pk>/delete/', views.delete_order,name='delete_order'),
    path('orders/coupon/validate/', views.validate_coupon, name='validate_coupon'),
    path('delivery-governorates/', views.get_governorates, name='delivery_governorates'
),
]   
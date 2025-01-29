from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register,name='register'),
    path('userinfo/', views.current_user,name='user_info'),
    path('userinfo/update/', views.update_user,name='update_user'),
    path('forgot_password/', views.forgot_password,name='forgot_password'),
    path('verify_reset_token/<str:token>', views.verify_reset_token,name='verify_reset_token'),
    path('reset_password/<str:token>', views.reset_password,name='reset_password'),
    path('get_phone_number/', views.get_phone_number, name='get_phone_number'),
    path('get_delivery_Cost/', views.get_delivery_Cost, name='get_delivery_Cost'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('get_user_type/', views.get_user_type, name='get_user_type'),
    path('google_login/', views.google_login, name='google_login'),
] 
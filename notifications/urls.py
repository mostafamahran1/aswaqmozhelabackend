from django.urls import path

from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='notification_inbox'),
    path('inbox/read/', views.mark_inbox_read, name='notification_inbox_read'),
    path('presence/', views.customer_presence, name='customer_presence'),
    path('announce/', views.announce, name='announce'),
]

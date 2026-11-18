from django.urls import path

from . import views

urlpatterns = [
    path('cards/', views.card_ratings, name='card_ratings'),
    path('product/', views.product_reviews, name='product_reviews'),
    path('product/rate/', views.rate_product, name='rate_product'),
    path('app/', views.rate_app, name='rate_app'),
]

from django.contrib import admin

from .models import AppFeedback, ProductReview

admin.site.register(ProductReview)
admin.site.register(AppFeedback)

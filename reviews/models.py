from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from order.models import Order


class ProductReview(models.Model):
    model_name = models.CharField(max_length=50)
    product_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.CharField(max_length=500, blank=True, default='')
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'model_name', 'product_id'],
                name='one_review_per_product',
            ),
        ]
        indexes = [
            models.Index(fields=['model_name', 'product_id', '-created_at']),
        ]


class AppFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_feedback')
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    rating = models.PositiveSmallIntegerField()
    suggestion = models.CharField(max_length=800, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'order'],
                condition=Q(order__isnull=False),
                name='one_feedback_per_order',
            ),
        ]

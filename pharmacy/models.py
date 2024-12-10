from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from allproducts.models import BaseProduct

class PharmacyProduct(BaseProduct):
    pass

    def __str__(self):
        return self.name

class PharmacyReview(models.Model):
    product = models.ForeignKey(PharmacyProduct, null=True, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    rating = models.IntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    createAT = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.comment


@receiver(post_save, sender=PharmacyProduct)
def update_product_image_path(sender, instance, created, **kwargs):
    if created:
        instance.save()

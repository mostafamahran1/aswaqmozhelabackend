from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Product(models.Model):
    name = models.CharField(max_length=50, default="", blank=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    primary_image = models.ImageField(upload_to='products/', blank=True, null=True)
    secondary_image1 = models.ImageField(upload_to='products/', blank=True, null=True)
    secondary_image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(max_length=1000, default="", blank=True, null=True)
    stock = models.IntegerField(default=0)
    createAT = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    delivery_days = models.IntegerField(default=3)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    rating = models.IntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    createAT = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.comment


@receiver(post_save, sender=Product)
def update_product_image_path(sender, instance, created, **kwargs):
    if created:
        instance.save()

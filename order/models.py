from django.db import models
from operator import mod
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class OrderStatus(models.TextChoices):
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELED = 'Canceled'

class PaymentStatus(models.TextChoices):
    PAID = 'Paid'
    UNPAID = 'Unpaid'
    
class PaymentMode(models.TextChoices):
    COD = 'COD'  # cash_on_delivered
    CARD = 'CARD'

class Order(models.Model):
    city = models.CharField(max_length=400,default="",blank=False)
    zip_code = models.CharField(max_length=100,default="",blank=False)
    street = models.CharField(max_length=500,default="",blank=False)
    state = models.CharField(max_length=100,default="",blank=False)
    country = models.CharField(max_length=1000,default="",blank=False)
    phone_no = models.CharField(max_length=100,default="",blank=False)
    total_amount = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=30,choices=PaymentStatus.choices,default=PaymentStatus.UNPAID)
    payment_mode = models.CharField(max_length=30,choices=PaymentMode.choices,default=PaymentMode.COD)
    status = models.CharField(max_length=60,choices=OrderStatus.choices,default=OrderStatus.PROCESSING)
    user = models.ForeignKey(User , null=True, on_delete=models.SET_NULL )
    createAT = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)
    


class OrderItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)  # جعل الحقل nullable
    object_id = models.PositiveIntegerField(null=True)  # جعل الحقل nullable
    product = GenericForeignKey('content_type', 'object_id')

    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE, related_name='orderitems')
    name = models.CharField(max_length=200, default="", blank=False)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)
    primary_image = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

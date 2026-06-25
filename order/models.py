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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=30,choices=PaymentStatus.choices,default=PaymentStatus.UNPAID)
    payment_mode = models.CharField(max_length=30,choices=PaymentMode.choices,default=PaymentMode.COD)
    status = models.CharField(max_length=60,choices=OrderStatus.choices,default=OrderStatus.PROCESSING)
    user = models.ForeignKey(User , null=True, on_delete=models.SET_NULL )
    createAT = models.DateTimeField(default=timezone.now)
    coupon = models.ForeignKey('Coupon', null=True, blank=True, on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.id)
    


class OrderItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)  # جعل الحقل nullable
    object_id = models.PositiveIntegerField(null=True)  # جعل الحقل nullable
    product = GenericForeignKey('content_type', 'object_id')

    # 🔗 الربط مع المتغير المحدد (يجوز أن يكون فارغاً لو المنتج ملوش ألوان/مقاسات)
    variant = models.ForeignKey('allproducts.ProductVariant', null=True, blank=True, on_delete=models.SET_NULL, related_name='order_items')
    
    # 📸 كاش لحفظ تفاصيل المتغير وقت الشراء لحماية الفواتير القديمة من التعديل
    color_name = models.CharField(max_length=100, blank=True, null=True)
    color_code = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)

    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE, related_name='orderitems')
    name = models.CharField(max_length=200, default="", blank=False)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)
    primary_image = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.color_name or 'No Variant'})"

# models.py

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField(default=0)  # مثال 10%
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.code
    

class DeliveryGovernorate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.delivery_fee} EGP"
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
# استيراد الأدوات الخاصة بالـ Generic Relations
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey , GenericRelation

class BaseProduct(models.Model):
    MODEL_NAME_CHOICES = [
        ('Phones', 'Phones'),
        ('Shein', 'Shein'),
        ('Foods', 'Foods'),
        ('Fav', 'Fav'),
        ('Pharmacy', 'Pharmacy'),
        ('Spices', 'Spices'),
        ('Supermarket', 'Supermarket'),
        ('Toys', 'Toys'),
        ('Veils', 'Veils'),
        ('Socks', 'Socks'),
        ('Birthday', 'Birthday'),
        ('Gifts', 'Gifts'),
        ('Accessories', 'Accessories'),
        ('Library', 'Library')
    ]
    
    name = models.CharField(max_length=100, default="", blank=False)
    model_name = models.CharField(max_length=50, choices=MODEL_NAME_CHOICES, default='Supermarket')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)#السعر بعد الخصم 
    original_price = models.DecimalField(max_digits=6, decimal_places=2, default=0) #السعر قبل الخصم
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0) #نسبة الخصم
    primary_image = models.ImageField(upload_to='products/', blank=True, null=True)
    secondary_image1 = models.ImageField(upload_to='products/', blank=True, null=True)
    secondary_image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(max_length=1000, default="", blank=True, null=True)
    stock = models.IntegerField(default=0)
    createAT = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    delivery_days = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    orders_count = models.IntegerField(default=0)
    variants = GenericRelation('allproducts.ProductVariant', related_query_name='product')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        try:
            discount = float(self.discount_percentage)
            original = float(self.original_price)
            if discount > 0 and original > 0:
                self.price = original - (original * discount / 100)
            else:
                self.price = original
        except (ValueError, TypeError):
            self.price = 0  # أو أي قيمة افتراضية
        super().save(*args, **kwargs)


    class Meta:
        abstract = True  # هذا يجعل النموذج مجرد قاعدة ولن يتم إنشاء جدول له في قاعدة البيانات

class ProductVariant(models.Model):
    # --- إعداد الربط الديناميكي ---
    # يحدد الموديل المستهدف (مثل: GiftsProduct أو ToysProduct)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # يخزن الـ ID الخاص بالمنتج داخل الجدول بتاعه
    object_id = models.PositiveIntegerField()
    # الحقل السحري اللي بيجمعهم ويخليك تتعامل مع المنتج مباشرة
    content_object = GenericForeignKey('content_type', 'object_id')

    # --- خصائص المتغير (اللون والمقاس) ---
    color_name = models.CharField(max_length=50, verbose_name="اسم اللون (مثال: ذهبي، فضي، أحمر)")
    color_code = models.CharField(max_length=7, blank=True, null=True, verbose_name="كود اللون الهيكس (اختياري مثل: #FFFFFF)")
    size = models.CharField(max_length=30, blank=True, null=True, verbose_name="المقاس (اختياري)")

    # --- الصور الثلاثة الخاصة بكل متغير (لون) ---
    variant_image1 = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    variant_image2 = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    variant_image3 = models.ImageField(upload_to='products/variants/', blank=True, null=True)

    # --- الأسعار والمخزون الخاصة بهذا المتغير بالذات ---
    original_price = models.DecimalField(max_digits=6, decimal_places=2, default=0) # السعر قبل الخصم
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0) # نسبة الخصم
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0) # السعر النهائي بعد الخصم (يتم حسابه تلقائياً)
    stock = models.IntegerField(default=0) # كمية المخزون من اللون ده بالذات
    
    is_active = models.BooleanField(default=True)
    createAT = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # نفس منطق الحساب التلقائي للسعر اللي عندك
        try:
            discount = float(self.discount_percentage)
            original = float(self.original_price)
            if discount > 0 and original > 0:
                self.price = original - (original * discount / 100)
            else:
                self.price = original
        except (ValueError, TypeError):
            self.price = 0
        super().save(*args, **kwargs)

    def __str__(self):
        # هيعرض في الأدمين اسم المنتج الأساسي وجنبه اللون والمقاس
        return f"{self.content_object} - {self.color_name} ({self.size or 'بدون مقاس'})"
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from allproducts.models import ProductVariant
from .models import BirthdayProduct


# 1. جدول المتغيرات المدمج
class ProductVariantInline(GenericTabularInline):
    model = ProductVariant
    extra = 1
    fields = [
        'color_name', 'color_code', 'size', 
        'original_price', 'discount_percentage', 'stock', 
        'variant_image1', 'variant_image2', 'variant_image3'
    ]

@admin.register(BirthdayProduct)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'price','original_price', 'discount_percentage', 'stock', 'createAT', 'user')
    search_fields = ('name', 'description')
    list_filter = ('createAT', 'user')

    # 2. أضفنا السطر ده هنا لربط الجدول
    inlines = [ProductVariantInline]


from django.contrib import admin
from .models import Image, TopBannerImage # استيراد الموديل الجديد هنا

# تسجيل الجدول القديم بتاعك زي ما هو بدون تغيير في خواصه
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'image']

# 🚀 تسجيل الجدول الجديد الخاص بالبانر العلوي الإعلاني
@admin.register(TopBannerImage)
class TopBannerImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'image', 'created_at']
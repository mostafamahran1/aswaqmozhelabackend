from rest_framework import serializers
from .models import Image, TopBannerImage # 1. استيراد الموديل الجديد هنا

# الـ Serializer القديم بتاعك زي ما هو بدون تعديل
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

# 🚀 الـ Serializer الجديد الخاص بالبانر العلوي الإعلاني
class TopBannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopBannerImage
        fields = '__all__' # أو حدد الحقول ['id', 'title', 'image'] لو مش عايز وقت الرفع يرجع تاريخ الإنشاء
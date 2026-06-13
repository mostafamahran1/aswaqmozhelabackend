from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response  # تأكد من استيراد Response
from .models import Image
from django.shortcuts import render
from .serializers import ImageSerializer
from .models import TopBannerImage # استيراد الموديل الجديد
from .serializers import TopBannerImageSerializer # أو استخدم نفس السيريالايزر القديم لو حابب


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # إضافة عدد الصور إلى الاستجابة
        return Response({
            "images": serializer.data,
            "count": queryset.count()  # استخدام queryset.count() للحصول على عدد الصور
        })

def home(request):
    return render(request, 'home.html')

class TopBannerViewSet(viewsets.ModelViewSet):
    queryset = TopBannerImage.objects.all() # يقرأ من جدول الإعلانات العلوي الجديد 🎯
    serializer_class = ImageSerializer # تقدر تسيب نفس السيريالايزر عادي لأنه مجرد بيعرض العنوان والصورة
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "images": serializer.data,
            "count": queryset.count()
        })
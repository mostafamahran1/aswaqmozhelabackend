from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response  # تأكد من استيراد Response
from .models import Image
from django.shortcuts import render
from .serializers import ImageSerializer

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
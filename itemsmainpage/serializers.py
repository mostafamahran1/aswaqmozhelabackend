from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url']  # لا حاجة لإرجاع الحقل 'image' لأنه سيتم تحويله إلى رابط كامل

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return ''

from rest_framework import serializers
from .models import Allproduct, Allreview

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allreview
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)
    primary_image = serializers.SerializerMethodField(method_name='get_primary_image', read_only=True)
    secondary_image1 = serializers.SerializerMethodField(method_name='get_secondary_image1', read_only=True)
    secondary_image2 = serializers.SerializerMethodField(method_name='get_secondary_image2', read_only=True)

    class Meta:
        model = Allproduct
        fields = "__all__"

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

    def get_primary_image(self, obj):
        request = self.context.get('request')
        if obj.primary_image:
            return request.build_absolute_uri(obj.primary_image.url)
        return None

    def get_secondary_image1(self, obj):
        request = self.context.get('request')
        if obj.secondary_image1:
            return request.build_absolute_uri(obj.secondary_image1.url)
        return None

    def get_secondary_image2(self, obj):
        request = self.context.get('request')
        if obj.secondary_image2:
            return request.build_absolute_uri(obj.secondary_image2.url)
        return None

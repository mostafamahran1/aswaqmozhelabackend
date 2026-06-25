from rest_framework import serializers
from .models import PharmacyProduct, PharmacyReview
from allproducts.models import ProductVariant

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyReview
        fields = "__all__"

# 1. السيندر الجديد الخاص بالألوان والمتغيرات
class ProductVariantSerializer(serializers.ModelSerializer):
    variant_image1 = serializers.SerializerMethodField()
    variant_image2 = serializers.SerializerMethodField()
    variant_image3 = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = "__all__"

    def get_variant_image1(self, obj):
        request = self.context.get('request')
        if obj.variant_image1 and request:
            return request.build_absolute_uri(obj.variant_image1.url)
        return None

    def get_variant_image2(self, obj):
        request = self.context.get('request')
        if obj.variant_image2 and request:
            return request.build_absolute_uri(obj.variant_image2.url)
        return None

    def get_variant_image3(self, obj):
        request = self.context.get('request')
        if obj.variant_image3 and request:
            return request.build_absolute_uri(obj.variant_image3.url)
        return None


class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)
    # 2. السطر السحري: جلب قائمة المتغيرات (الألوان والمقاسات والصور التابعة للمنتج)
    variants = ProductVariantSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField(method_name='get_primary_image', read_only=True)
    secondary_image1 = serializers.SerializerMethodField(method_name='get_secondary_image1', read_only=True)
    secondary_image2 = serializers.SerializerMethodField(method_name='get_secondary_image2', read_only=True)

    class Meta:
        model = PharmacyProduct
        fields = "__all__"

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

    def get_primary_image(self, obj):
        request = self.context.get('request', None)
        if obj.primary_image and request:  # Ensure the image exists and request is provided
            return request.build_absolute_uri(obj.primary_image.url)
        return None

    def get_secondary_image1(self, obj):
        request = self.context.get('request', None)
        if obj.secondary_image1 and request:  # Ensure the image exists and request is provided
            return request.build_absolute_uri(obj.secondary_image1.url)
        return None

    def get_secondary_image2(self, obj):
        request = self.context.get('request', None)
        if obj.secondary_image2 and request:  # Ensure the image exists and request is provided
            return request.build_absolute_uri(obj.secondary_image2.url)
        return None


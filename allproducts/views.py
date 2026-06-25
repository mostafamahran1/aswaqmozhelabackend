import heapq
import random
import json
from django.http import JsonResponse
from django.db.models import Q
from django.templatetags.static import static
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

# استيراد الموديلات الخاصة بك
from .models import BaseProduct
from phones.models import PhonesProduct
from shein.models import SheinProduct
from foods.models import FoodsProduct
from fruitsandvegetables.models import FavProduct
from pharmacy.models import PharmacyProduct
from products.models import LibraryProduct
from spices.models import SpicesProduct
from supermarket.models import SupermarketProduct
from toys.models import ToysProduct
from accessories.models import AccessoriesProduct
from gifts.models import GiftsProduct
from birthday.models import BirthdayProduct
from socks.models import SocksProduct
from veils.models import VeilsProduct

# استيراد موديل الـ Variant (تأكد من المسار الصحيح له في مشروعك)
from allproducts.models import ProductVariant 

MODEL_MAPPING = {
    'Phones': PhonesProduct,
    'Clothes': SheinProduct,
    'Foods': FoodsProduct,
    'Fav': FavProduct,
    'Pharmacy': PharmacyProduct,
    'Library': LibraryProduct,
    'Spices': SpicesProduct,
    'Supermarket': SupermarketProduct,
    'Toys': ToysProduct,
    'Accessories': AccessoriesProduct,
    'Gifts': GiftsProduct,
    'Birthday': BirthdayProduct,
    'Socks': SocksProduct,
    'Veils': VeilsProduct,
}


class GetModelNames(APIView):
    def get(self, request):
        model_name_choices = [{"value": key, "label": value} for key, value in BaseProduct.MODEL_NAME_CHOICES]
        return Response(model_name_choices, status=status.HTTP_200_OK)


# 🌟 دالة مساعدة سحرية لجلب وتنسيق الـ Variants لأي منتج من الـ 14 موديل وإرسالها للفرونت إند
def get_product_variants_list(product, request):
    variants_data = []
    # جلب المتغيرات النشطة التابعة لهذا المنتج ديناميكياً
    for variant in product.variants.filter(is_active=True):
        variants_data.append({
            'id': variant.id,
            'color_name': variant.color_name,
            'color_code': variant.color_code,
            'size': variant.size,
            'variant_image1': request.build_absolute_uri(variant.variant_image1.url) if variant.variant_image1 else None,
            'variant_image2': request.build_absolute_uri(variant.variant_image2.url) if variant.variant_image2 else None,
            'variant_image3': request.build_absolute_uri(variant.variant_image3.url) if variant.variant_image3 else None,
            'original_price': float(variant.original_price),
            'discount_percentage': float(variant.discount_percentage),
            'price': float(variant.price),
            'stock': variant.stock,
            'is_active': variant.is_active,
        })
    return variants_data


def search_all_products(request):
    query = request.GET.get('name', '')
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    category = request.GET.get('category', None)

    if not query and not min_price and not max_price and not category:
        return JsonResponse({"products": []})

    models = list(MODEL_MAPPING.values())
    products = []

    for model in models:
        filters = Q()
        if query:
            filters &= (Q(name__icontains=query) | Q(description__icontains=query) | Q(model_name__icontains=query))
        if min_price:
            filters &= Q(price__gte=float(min_price))
        if max_price:
            filters &= Q(price__lte=float(max_price))
        if category and category.strip() != "":
            filters &= Q(model_name__iexact=category)

        # 🛑 تم إزالة .values() واستبدالها بـ prefetch_related لدعم الـ GenericRelation للألوان
        results = model.objects.filter(filters).prefetch_related('variants')

        for product in results:
            product_data = {
                'id': product.id,
                'name': product.name,
                'model_name': product.model_name,
                'price': float(product.price),
                'original_price': float(product.original_price),
                'discount_percentage': float(product.discount_percentage),
                'createAT': product.createAT,
                'primary_image': request.build_absolute_uri(product.primary_image.url) if product.primary_image else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image1': request.build_absolute_uri(product.secondary_image1.url) if product.secondary_image1 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image2': request.build_absolute_uri(product.secondary_image2.url) if product.secondary_image2 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'description': product.description,
                'stock': product.stock,
                'delivery_days': product.delivery_days,
                'is_active': product.is_active,
                'is_available': product.is_available,
                'user': product.user.id if product.user else None,
                'variants': get_product_variants_list(product, request)  # 🔥 هنا ربطنا المتغيرات بالبحث
            }
            products.append(product_data)

    return JsonResponse({"products": products})


def get_latest_products(request):
    count = int(request.GET.get('count', 100))
    models = list(MODEL_MAPPING.values())
    all_products = []

    for model in models:
        # تحسين الأداء باستخدام prefetch_related
        products = model.objects.all().prefetch_related('variants').order_by('-createAT')[:count]
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'model_name': product.model_name,
                'price': float(product.price),
                'original_price': float(product.original_price),
                'discount_percentage': float(product.discount_percentage),
                'createAT': product.createAT,
                'primary_image': request.build_absolute_uri(product.primary_image.url) if product.primary_image else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image1': request.build_absolute_uri(product.secondary_image1.url) if product.secondary_image1 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image2': request.build_absolute_uri(product.secondary_image2.url) if product.secondary_image2 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'description': product.description,
                'stock': product.stock,
                'delivery_days': product.delivery_days,
                'is_active': product.is_active,
                'is_available': product.is_available,
                'user': product.user.id if product.user else None,
                'variants': get_product_variants_list(product, request)  # 🔥 أضفنا المتغيرات هنا للرئيسية
            }
            all_products.append(product_data)

    latest_subset = heapq.nlargest(count, all_products, key=lambda x: x['createAT'])
    random.shuffle(latest_subset)

    return JsonResponse({'products': latest_subset})


def get_discounted_products(request):
    count = int(request.GET.get('count', 100))
    models = list(MODEL_MAPPING.values())
    discounted_products = []

    for model in models:
        products = model.objects.filter(discount_percentage__gt=0).prefetch_related('variants').order_by('-createAT')[:count]
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'model_name': product.model_name,
                'price': float(product.price),
                'original_price': float(product.original_price),
                'discount_percentage': float(product.discount_percentage),
                'createAT': product.createAT,
                'primary_image': request.build_absolute_uri(product.primary_image.url) if product.primary_image else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image1': request.build_absolute_uri(product.secondary_image1.url) if product.secondary_image1 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image2': request.build_absolute_uri(product.secondary_image2.url) if product.secondary_image2 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'description': product.description,
                'stock': product.stock,
                'delivery_days': product.delivery_days,
                'is_active': product.is_active,
                'is_available': product.is_available,
                'user': product.user.id if product.user else None,
                'variants': get_product_variants_list(product, request)  # 🔥 أضفنا المتغيرات هنا لصفحة الخصومات
            }
            discounted_products.append(product_data)

    discounted_subset = heapq.nlargest(count, discounted_products, key=lambda x: x['createAT'])
    random.shuffle(discounted_subset)

    return JsonResponse({'products': discounted_subset})


def get_best_selling_products(request):
    count = int(request.GET.get('count', 20))
    models = list(MODEL_MAPPING.values())
    best_selling_products = []

    for model in models:
        products = model.objects.filter(is_available=True, is_active=True).prefetch_related('variants').order_by('-orders_count')[:count]
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'model_name': product.model_name,
                'price': float(product.price),
                'original_price': float(product.original_price),
                'discount_percentage': float(product.discount_percentage),
                'createAT': product.createAT,
                'orders_count': product.orders_count,
                'primary_image': request.build_absolute_uri(product.primary_image.url) if product.primary_image else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image1': request.build_absolute_uri(product.secondary_image1.url) if product.secondary_image1 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image2': request.build_absolute_uri(product.secondary_image2.url) if product.secondary_image2 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'description': product.description,
                'stock': product.stock,
                'delivery_days': product.delivery_days,
                'is_active': product.is_active,
                'is_available': product.is_available,
                'user': product.user.id if product.user else None,
                'variants': get_product_variants_list(product, request)  # 🔥 أضفنا المتغيرات هنا للأكثر مبيعاً
            }
            best_selling_products.append(product_data)

    sorted_best_sellers = heapq.nlargest(count, best_selling_products, key=lambda x: x['orders_count'])

    return JsonResponse({'products': sorted_best_sellers})
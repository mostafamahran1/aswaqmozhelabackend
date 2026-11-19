import heapq
import random
import json
from django.http import JsonResponse
from django.db.models import Q
from django.templatetags.static import static
from .search_text import score_product
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


def _search_by_text(request, models, query, min_price, max_price, category):
    ranked = []
    for model in models:
        queryset = model.objects.all()
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
        if category and category.strip() != '':
            queryset = queryset.filter(model_name__iexact=category)
        for row in queryset.values('id', 'name', 'description', 'model_name'):
            score = score_product(query, row['name'], row['description'], row['model_name'])
            if score > 0:
                ranked.append((score, model, row['id']))

    ranked.sort(key=lambda item: item[0], reverse=True)
    chosen = ranked[:40]
    grouped = {}
    for _score, model, pk in chosen:
        grouped.setdefault(model, []).append(pk)

    loaded = {}
    for model, ids in grouped.items():
        for product in model.objects.filter(id__in=ids).prefetch_related('variants'):
            loaded[(model, product.id)] = product

    products = []
    for _score, model, pk in chosen:
        product = loaded.get((model, pk))
        if product is not None:
            products.append(_product_payload(product, request))
    return products


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
        if query:
            continue
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
                'is_active': product.is_active,
                'is_available': product.is_available,
                'user': product.user.id if product.user else None,
                'variants': get_product_variants_list(product, request)  # 🔥 هنا ربطنا المتغيرات بالبحث
            }
            products.append(product_data)

    if query:
        products = _search_by_text(request, models, query, min_price, max_price, category)

    return JsonResponse({"products": products})


def _product_payload(product, request, include_orders=False):
    placeholder = request.build_absolute_uri(static('products/placeholder.jpg'))

    def image_url(field_file):
        if field_file:
            return request.build_absolute_uri(field_file.url)
        return placeholder

    payload = {
        'id': product.id,
        'name': product.name,
        'model_name': product.model_name,
        'price': float(product.price),
        'original_price': float(product.original_price),
        'discount_percentage': float(product.discount_percentage),
        'createAT': product.createAT,
        'primary_image': image_url(product.primary_image),
        'secondary_image1': image_url(product.secondary_image1),
        'secondary_image2': image_url(product.secondary_image2),
        'description': product.description,
        'stock': product.stock,
        'is_active': product.is_active,
        'is_available': product.is_available,
        'user': product.user.id if product.user else None,
        'variants': get_product_variants_list(product, request),
    }
    if include_orders:
        payload['orders_count'] = product.orders_count
    return payload


def _load_ranked_products(candidates, count):
    chosen = heapq.nlargest(count, candidates, key=lambda item: item[0])
    grouped = {}
    for _sort_value, model, pk in chosen:
        grouped.setdefault(model, []).append(pk)
    loaded = {}
    for model, ids in grouped.items():
        for product in model.objects.filter(id__in=ids).prefetch_related('variants'):
            loaded[(model, product.id)] = product
    products = []
    for _sort_value, model, pk in chosen:
        product = loaded.get((model, pk))
        if product is not None:
            products.append(product)
    return products


def get_latest_products(request):
    count = int(request.GET.get('count', 100))
    candidates = []
    for model in MODEL_MAPPING.values():
        rows = model.objects.order_by('-createAT').values_list('id', 'createAT')[:count]
        candidates.extend((created, model, pk) for pk, created in rows)

    products = _load_ranked_products(candidates, count)
    latest_subset = [_product_payload(product, request) for product in products]
    random.shuffle(latest_subset)
    return JsonResponse({'products': latest_subset})


def get_discounted_products(request):
    count = int(request.GET.get('count', 100))
    candidates = []
    for model in MODEL_MAPPING.values():
        rows = (
            model.objects.filter(discount_percentage__gt=0)
            .order_by('-createAT')
            .values_list('id', 'createAT')[:count]
        )
        candidates.extend((created, model, pk) for pk, created in rows)

    products = _load_ranked_products(candidates, count)
    discounted_subset = [_product_payload(product, request) for product in products]
    random.shuffle(discounted_subset)
    return JsonResponse({'products': discounted_subset})


def get_best_selling_products(request):
    count = int(request.GET.get('count', 20))
    candidates = []
    for model in MODEL_MAPPING.values():
        rows = (
            model.objects.filter(is_available=True, is_active=True)
            .order_by('-orders_count')
            .values_list('id', 'orders_count')[:count]
        )
        candidates.extend((orders_count, model, pk) for pk, orders_count in rows)

    products = _load_ranked_products(candidates, count)
    sorted_best_sellers = [
        _product_payload(product, request, include_orders=True) for product in products
    ]
    return JsonResponse({'products': sorted_best_sellers})


def get_similar_products(request):
    """
    جلب المنتجات المشابهة لمنتج معين من خلال الـ 14 موديل.
    يعتمد التشابه على نفس الـ model_name (القسم) مع استبعاد المنتج الحالي.
    """
    product_id_str = request.GET.get('product_id')
    model_name = request.GET.get('model_name')
    count = int(request.GET.get('count', 6)) # الافتراضي جلب 6 منتجات مشابهة

    # 1. التحقق من المدخلات الأساسية لتجنب الكراش
    if not product_id_str or not model_name:
        return JsonResponse({"products": [], "error": "Missing product_id or model_name parameters"}, status=400)

    try:
        product_id = int(product_id_str)
    except ValueError:
        return JsonResponse({"products": [], "error": "Invalid product_id"}, status=400)

    # 2. الحصول على الموديل الصحيح من الـ Mapping بناءً على الـ model_name المرسل
    target_model = MODEL_MAPPING.get(model_name)
    
    if not target_model:
        return JsonResponse({"products": []}) # إذا كان القسم غير معروف نرجع مصفوفة فارغة بأمان

    # 3. جلب المنتجات النشطة والمتاحة من نفس القسم واستبعاد المنتج الأصلي
    # similar products follow sales, which stays useful and avoids ORDER BY RANDOM()
    similar_results = target_model.objects.filter(
        model_name=model_name,
        is_active=True,
        is_available=True
    ).exclude(id=product_id).prefetch_related('variants').order_by('-orders_count')[:count]

    similar_products = []

    # 4. تنسيق البيانات بنفس بنية البيانات التي يتوقعها الـ Flutter الفرونت إند عندك
    for product in similar_results:
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
            'is_active': product.is_active,
            'is_available': product.is_available,
            'user': product.user.id if product.user else None,
            'variants': get_product_variants_list(product, request) # هنا استدعينا الدالة السحرية للألوان والمقاسات
        }
        similar_products.append(product_data)

    return JsonResponse({'products': similar_products})
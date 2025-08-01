import heapq
from django.http import JsonResponse
from django.db.models import Q
from django.templatetags.static import static
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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


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


def search_all_products(request):
    query = request.GET.get('name', '')
    if not query:
        return JsonResponse({"products": []})

    models = [
        PhonesProduct, SheinProduct, FoodsProduct, FavProduct, PharmacyProduct, LibraryProduct,
        SpicesProduct, SupermarketProduct, ToysProduct, AccessoriesProduct, GiftsProduct,
        BirthdayProduct, SocksProduct, VeilsProduct
    ]

    products = []

    for model in models:
        results = model.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(model_name__icontains=query)
        ).values()

        for product in results:
            if product['primary_image']:
                product['primary_image'] = request.build_absolute_uri(settings.MEDIA_URL + product['primary_image'])
            else:
                product['primary_image'] = request.build_absolute_uri(static('products/placeholder.jpg'))
            products.append(product)

    return JsonResponse({"products": products})


def get_latest_products(request):
    count = int(request.GET.get('count', 100))  # Default to 10 if not provided

    models = [
        PhonesProduct, SheinProduct, FoodsProduct, FavProduct, PharmacyProduct, LibraryProduct,
        SpicesProduct, SupermarketProduct, ToysProduct, AccessoriesProduct, GiftsProduct,
        BirthdayProduct, SocksProduct, VeilsProduct
    ]

    all_products = []

    for model in models:
        products = model.objects.all().order_by('-createAT')[:count]
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'model_name': product.model_name,
                'price': product.price,
                'original_price': product.original_price,
                'discount_percentage': product.discount_percentage,
                'createAT': product.createAT,
                'primary_image': request.build_absolute_uri(product.primary_image.url) if product.primary_image else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image1': request.build_absolute_uri(product.secondary_image1.url) if product.secondary_image1 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image2': request.build_absolute_uri(product.secondary_image2.url) if product.secondary_image2 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'description': product.description,
                'stock': product.stock,
                'delivery_days': product.delivery_days,
                'is_active': product.is_active,
                'is_available': product.is_available,
                'user': product.user.id if product.user else None
            }
            all_products.append(product_data)

    sorted_products = heapq.nlargest(count, all_products, key=lambda x: x['createAT'])

    return JsonResponse({'products': sorted_products})


def get_discounted_products(request):
    count = int(request.GET.get('count', 100))  # عدد المنتجات اللي هترجعها، افتراضي 100

    models = [
        PhonesProduct, SheinProduct, FoodsProduct, FavProduct, PharmacyProduct, LibraryProduct,
        SpicesProduct, SupermarketProduct, ToysProduct, AccessoriesProduct, GiftsProduct,
        BirthdayProduct, SocksProduct, VeilsProduct
    ]

    discounted_products = []

    for model in models:
        products = model.objects.filter(discount_percentage__gt=0).order_by('-createAT')[:count]
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'model_name': product.model_name,
                'price': product.price,
                'original_price': product.original_price,
                'discount_percentage': product.discount_percentage,
                'createAT': product.createAT,
                'primary_image': request.build_absolute_uri(product.primary_image.url) if product.primary_image else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image1': request.build_absolute_uri(product.secondary_image1.url) if product.secondary_image1 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'secondary_image2': request.build_absolute_uri(product.secondary_image2.url) if product.secondary_image2 else request.build_absolute_uri(static('products/placeholder.jpg')),
                'description': product.description,
                'stock': product.stock,
                'delivery_days': product.delivery_days,
                'is_active': product.is_active,
                'is_available': product.is_available,
                'user': product.user.id if product.user else None
            }
            discounted_products.append(product_data)

    # ترتيب كل المنتجات المجمعة من جميع الموديلات حسب تاريخ الإنشاء
    sorted_discounted_products = heapq.nlargest(count, discounted_products, key=lambda x: x['createAT'])

    return JsonResponse({'products': sorted_discounted_products})

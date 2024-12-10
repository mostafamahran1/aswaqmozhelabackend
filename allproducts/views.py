from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from django.templatetags.static import static
from .models import BaseProduct
from phones.models import PhonesProduct
from clothes.models import ClothesProduct
from foods.models import FoodsProduct
from fruitsandvegetables.models import FavProduct
from pharmacy.models import PharmacyProduct
from products.models import Product
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



class GetModelNames(APIView):
    def get(self, request):
        model_name_choices = dict(BaseProduct.MODEL_NAME_CHOICES)
        return Response(model_name_choices, status=status.HTTP_200_OK)

def search_all_products(request):
    query = request.GET.get('name', '')
    if not query:
        return JsonResponse({"products": []})
    
    phones = PhonesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(model_name__icontains=query))
    clothes = ClothesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(model_name__icontains=query) )
    foods = FoodsProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    fav = FavProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    pharmacy = PharmacyProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    libraryproducts = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    spices = SpicesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    supermarket = SupermarketProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    toys = ToysProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    accessories = AccessoriesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    gifts = GiftsProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    birthday = BirthdayProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    socks = SocksProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))
    veils = VeilsProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)| Q(model_name__icontains=query))

    # Include 'description' field in the query
    products = list(phones.values()) + \
               list(clothes.values()) + \
               list(fav.values()) + \
               list(pharmacy.values()) + \
               list(libraryproducts.values()) + \
               list(spices.values()) + \
               list(supermarket.values()) + \
               list(toys.values()) + \
               list(accessories.values()) + \
               list(gifts.values()) + \
               list(birthday.values()) + \
               list(socks.values()) + \
               list(veils.values()) + \
               list(foods.values())
    # Convert image paths to absolute URLs
    for product in products:
        if product['primary_image']:
            product['primary_image'] = request.build_absolute_uri(settings.MEDIA_URL + product['primary_image'])
        else:
            product['primary_image'] = request.build_absolute_uri(static('products/placeholder.jpg'))

    return JsonResponse({"products": products})

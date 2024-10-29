from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from django.templatetags.static import static
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

def search_all_products(request):
    query = request.GET.get('name', '')
    if not query:
        return JsonResponse({"products": []})
    
    phones = PhonesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    clothes = ClothesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    foods = FoodsProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    fav = FavProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    pharmacy = PharmacyProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    libraryproducts = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    spices = SpicesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    supermarket = SupermarketProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    toys = ToysProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    accessories = AccessoriesProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    gifts = GiftsProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    birthday = BirthdayProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    socks = SocksProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    veils = VeilsProduct.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Include 'description' field in the query
    products = list(phones.values('name', 'price', 'primary_image', 'description')) + \
               list(clothes.values('name', 'price', 'primary_image', 'description')) + \
               list(fav.values('name', 'price', 'primary_image', 'description')) + \
               list(pharmacy.values('name', 'price', 'primary_image', 'description')) + \
               list(libraryproducts.values('name', 'price', 'primary_image', 'description')) + \
               list(spices.values('name', 'price', 'primary_image', 'description')) + \
               list(supermarket.values('name', 'price', 'primary_image', 'description')) + \
               list(toys.values('name', 'price', 'primary_image', 'description')) + \
               list(accessories.values('name', 'price', 'primary_image', 'description')) + \
               list(gifts.values('name', 'price', 'primary_image', 'description')) + \
               list(birthday.values('name', 'price', 'primary_image', 'description')) + \
               list(socks.values('name', 'price', 'primary_image', 'description')) + \
               list(veils.values('name', 'price', 'primary_image', 'description')) + \
               list(foods.values('name', 'price', 'primary_image', 'description'))

    # Convert image paths to absolute URLs
    for product in products:
        if product['primary_image']:
            product['primary_image'] = request.build_absolute_uri(settings.MEDIA_URL + product['primary_image'])
        else:
            product['primary_image'] = request.build_absolute_uri(static('products/placeholder.jpg'))

    return JsonResponse({"products": products})

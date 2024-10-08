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

def search_all_products(request):
    query = request.GET.get('name', '')
    if not query:
        return JsonResponse({"products": []})
    
    phones = PhonesProduct.objects.filter(name__icontains=query)
    clothes = ClothesProduct.objects.filter(name__icontains=query)
    foods = FoodsProduct.objects.filter(name__icontains=query)
    fav = FavProduct.objects.filter(name__icontains=query)
    pharmacy = PharmacyProduct.objects.filter(name__icontains=query)
    libraryproducts = Product.objects.filter(name__icontains=query)
    spices = SpicesProduct.objects.filter(name__icontains=query)
    supermarket = SupermarketProduct.objects.filter(name__icontains=query)
    toys = ToysProduct.objects.filter(name__icontains=query)

    # Combine all products
    products = list(phones.values('name', 'price', 'primary_image')) + \
               list(clothes.values('name', 'price', 'primary_image')) + \
               list(fav.values('name', 'price', 'primary_image')) + \
               list(pharmacy.values('name', 'price', 'primary_image')) + \
               list(libraryproducts.values('name', 'price', 'primary_image')) + \
               list(spices.values('name', 'price', 'primary_image')) + \
               list(supermarket.values('name', 'price', 'primary_image')) + \
               list(toys.values('name', 'price', 'primary_image')) + \
               list(foods.values('name', 'price', 'primary_image'))

    # Convert the local file path to a full URL
    for product in products:
        if product['primary_image']:
            # Ensure the path is correct
            product['primary_image'] = request.build_absolute_uri(settings.MEDIA_URL + product['primary_image'])
        else:
            # Provide a placeholder image if primary_image is missing
            product['primary_image'] = request.build_absolute_uri(static('products/placeholder.jpg'))

    return JsonResponse({"products": products})

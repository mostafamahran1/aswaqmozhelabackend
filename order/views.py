from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework import status
from products.models import Product
from django.db import transaction
from clothes.models import ClothesProduct
from foods.models import FoodsProduct
from fruitsandvegetables.models import FavProduct
from pharmacy.models import PharmacyProduct
from phones.models import PhonesProduct
from products.models import Product
from spices.models import SpicesProduct
from django.contrib.contenttypes.models import ContentType
from supermarket.models import SupermarketProduct
from toys.models import ToysProduct
from .serializers import OrderSerializer
from .models import Order,OrderItem
# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders,many = True)
    return Response({'orders':serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    serializer = OrderSerializer(orders, many=True)
    return Response({'orders': serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request,pk):
    order = get_object_or_404(Order , id = pk)

    serializer = OrderSerializer(order,many = False)
    return Response({'order':serializer.data})


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def process_order(request,pk):
    order = get_object_or_404(Order , id = pk)
    order.status = request.data['status']
    order.save()

    serializer = OrderSerializer(order,many = False)
    return Response({'order':serializer.data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_order(request,pk):
    order = get_object_or_404(Order , id = pk)
    order.delete()

    return Response({'order':"order is deleted"})


def calculate_delivery_fee(state):
    delivery_fee = 0
    
    if state == 'California':
        delivery_fee = 10.0
    elif state == 'New York':
        delivery_fee = 15.0
    else:
        delivery_fee = 25.0 
    
    return delivery_fee





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_order(request):
    user = request.user
    data = request.data
    print("User creating the order:", user.first_name, user.last_name)
    print("Received data:", data) 
    order_items = data.get('order_Items', [])
    
    if not order_items:
        return Response({'error': 'No order items received'}, status=status.HTTP_400_BAD_REQUEST)
    
    state = data.get('state', 'default_state')

    try:
        total_amount = sum(item['price'] * item['quantity'] for item in order_items)
        print("Total amount calculated:", total_amount)

        # حساب تكلفة التوصيل
        delivery_fee = calculate_delivery_fee(state)
        print("Delivery fee calculated:", delivery_fee)
        
        # إضافة تكلفة التوصيل إلى المجموع الكلي
        total_amount += delivery_fee

    except KeyError as e:
        print(f"Missing key in order items: {e}")
        return Response({'error': f'Missing key in order items: {e}'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                city=data['city'],
                zip_code=data['zip_code'],
                street=data['street'],
                state=state,
                phone_no=data['phone_no'],
                country=data['country'],
                total_amount=total_amount,
            )
            print("Order created successfully:", order.id)
            
            for i in order_items:
                product_id = i['product']
                
                product = (ClothesProduct.objects.filter(id=product_id).first() or
                           FoodsProduct.objects.filter(id=product_id).first() or
                           FavProduct.objects.filter(id=product_id).first() or
                           PharmacyProduct.objects.filter(id=product_id).first() or
                           PhonesProduct.objects.filter(id=product_id).first() or
                           SpicesProduct.objects.filter(id=product_id).first() or
                           SupermarketProduct.objects.filter(id=product_id).first() or
                           ToysProduct.objects.filter(id=product_id).first() or
                           Product.objects.filter(id=product_id).first()
                           )
                
                if not product:
                    print(f"Product with ID {product_id} does not exist")
                    return Response({'error': f'Product with ID {product_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                print(f"Product found: {product.name}")
                
                item = OrderItem.objects.create(
                    content_type=ContentType.objects.get_for_model(product.__class__),
                    object_id=product.id,
                    order=order,
                    name=product.name,
                    quantity=i['quantity'],
                    price=i['price'],
                    primary_image=request.build_absolute_uri(product.primary_image.url) if product.primary_image else None
                )
                print(f"Order item created: {item.name}")
                
                product.stock -= item.quantity
                product.save()
    
            serializer = OrderSerializer(order, many=False)
            print("Order serialized successfully")
            return Response(serializer.data)

    except Exception as e:
        print(f"Error occurred: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

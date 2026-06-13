from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated , IsAdminUser , BasePermission
from rest_framework import status
from products.models import LibraryProduct
from django.db import transaction
from shein.models import SheinProduct
from foods.models import FoodsProduct
from fruitsandvegetables.models import FavProduct
from pharmacy.models import PharmacyProduct
from phones.models import PhonesProduct
from products.models import LibraryProduct
from spices.models import SpicesProduct
from django.contrib.contenttypes.models import ContentType
from supermarket.models import SupermarketProduct
from toys.models import ToysProduct
from veils.models import VeilsProduct
from socks.models import SocksProduct
from birthday.models import BirthdayProduct
from gifts.models import GiftsProduct
from accessories.models import AccessoriesProduct
from .serializers import OrderSerializer
from .models import Order,OrderItem,Coupon,DeliveryGovernorate
# Create your views here.


class IsSuperuserOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


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
@permission_classes([IsAuthenticated, IsSuperuserOrStaff])
def process_order(request,pk):
    order = get_object_or_404(Order , id = pk)
    order.status = request.data['status']
    order.save()

    serializer = OrderSerializer(order,many = False)
    return Response({'order':serializer.data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsSuperuserOrStaff])
def delete_order(request,pk):
    order = get_object_or_404(Order , id = pk)
    order.delete()

    return Response({'order':"order is deleted"})


def calculate_delivery_fee(state):

    governorate = DeliveryGovernorate.objects.filter(
        name__iexact=state
    ).first()

    if governorate:
        return float(governorate.delivery_fee)

    return 35.0

@api_view(['GET'])
@permission_classes([AllowAny])
def get_governorates(request):

    governorates = DeliveryGovernorate.objects.all().order_by('name')

    return Response({
        "governorates": [
            {
                "name": gov.name,
                "delivery_fee": gov.delivery_fee
            }
            for gov in governorates
        ]
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_order(request):
    user = request.user
    data = request.data

    order_items = data.get('order_Items', [])
    coupon_code = data.get('coupon_code', None)
    state = data.get('state', 'default_state')

    if not order_items:
        return Response(
            {'error': 'No order items received'},
            status=status.HTTP_400_BAD_REQUEST
        )

    product_model_map = {
        'Shein': SheinProduct,
        'Foods': FoodsProduct,
        'Fav': FavProduct,
        'Pharmacy': PharmacyProduct,
        'Phones': PhonesProduct,
        'Spices': SpicesProduct,
        'Supermarket': SupermarketProduct,
        'Toys': ToysProduct,
        'Veils': VeilsProduct,
        'Socks': SocksProduct,
        'Birthday': BirthdayProduct,
        'Gifts': GiftsProduct,
        'Accessories': AccessoriesProduct,
        'Library': LibraryProduct
    }

    try:
        with transaction.atomic():

            # ========================
            # 1️⃣ CALCULATE SUBTOTAL
            # ========================
            subtotal = 0

            for item in order_items:
                product_id = item['product']
                model_name = item['model_name']
                quantity = item['quantity']

                ProductModel = product_model_map.get(model_name)

                if not ProductModel:
                    return Response(
                        {'error': f'Invalid model name: {model_name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                product = ProductModel.objects.filter(id=product_id).first()

                if not product:
                    return Response(
                        {'error': f'Product not found: {product_id}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                subtotal += float(product.price) * quantity

            # ========================
            # 2️⃣ DELIVERY FEE
            # ========================
            delivery_fee = calculate_delivery_fee(state)

            total_amount = subtotal + delivery_fee

            # ========================
            # 3️⃣ COUPON SYSTEM
            # ========================
            coupon_obj = None
            discount = 0

            if coupon_code:
                try:
                    coupon_obj = Coupon.objects.get(
                        code=coupon_code,
                        is_active=True
                    )

                    from django.utils import timezone

                    if coupon_obj.expiry_date < timezone.now():
                        return Response(
                            {'error': 'Coupon expired'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if subtotal < coupon_obj.min_order_amount:
                        return Response(
                            {'error': 'Order does not meet minimum amount for this coupon'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if coupon_obj.discount_percent > 0:
                         discount = (subtotal * coupon_obj.discount_percent) / 100
                    else:
                        discount = min(
                            float(coupon_obj.discount_amount),
                            subtotal
                        )

                    total_amount = subtotal - discount + delivery_fee

                except Coupon.DoesNotExist:
                    return Response(
                        {'error': 'Invalid coupon'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # ========================
            # 4️⃣ CREATE ORDER
            # ========================
            order = Order.objects.create(
                user=user,
                city=data['city'],
                zip_code=data['zip_code'],
                street=data['street'],
                state=state,
                phone_no=data['phone_no'],
                country=data['country'],
                total_amount=total_amount,
                coupon=coupon_obj,
                discount_amount=discount
            )

            # ========================
            # 5️⃣ CREATE ORDER ITEMS
            # ========================
            for item in order_items:
                product_id = item['product']
                model_name = item['model_name']
                quantity = item['quantity']

                ProductModel = product_model_map.get(model_name)
                product = ProductModel.objects.get(id=product_id)

                OrderItem.objects.create(
                    content_type=ContentType.objects.get_for_model(product),
                    object_id=product.id,
                    order=order,
                    name=product.name,
                    quantity=quantity,
                    price=product.price,
                    primary_image=(
                        request.build_absolute_uri(product.primary_image.url)
                        if product.primary_image else None
                    )
                )

                # update stock
                product.stock -= quantity
                product.orders_count += quantity
                product.save()

            serializer = OrderSerializer(order)

            return Response({
                "order": serializer.data,
                "subtotal": subtotal,
                "delivery_fee": delivery_fee,
                "discount_amount": discount,
                "coupon_used": coupon_obj is not None,
                "total_amount": total_amount
            })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# 🔥 COUPON VALIDATION API
# ================================

from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_coupon(request):

    coupon_code = request.data.get("coupon_code")
    subtotal = float(request.data.get("subtotal", 0))

    if not coupon_code:
        return Response({
            "valid": False,
            "message": "Coupon is required"
        }, status=400)

    try:
        coupon = Coupon.objects.get(
            code=coupon_code,
            is_active=True
        )

        if coupon.expiry_date < timezone.now():
            return Response({
                "valid": False,
                "message": "Coupon expired"
            }, status=400)

        if subtotal < coupon.min_order_amount:
            return Response({
                "valid": False,
                "message": f"Minimum order is {coupon.min_order_amount}"
            }, status=400)

        return Response({
            "valid": True,
            "code": coupon.code,
            "discount_percent": coupon.discount_percent,
            "discount_amount": coupon.discount_amount,
            "message": "Coupon applied successfully"
        })

    except Coupon.DoesNotExist:
        return Response({
            "valid": False,
            "message": "Invalid coupon"
        }, status=404)
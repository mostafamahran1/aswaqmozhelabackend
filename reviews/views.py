from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from order.models import Order, OrderItem
from .models import AppFeedback, ProductReview

PRODUCT_MODELS = None


def _models():
    global PRODUCT_MODELS
    if PRODUCT_MODELS is None:
        from accessories.models import AccessoriesProduct
        from birthday.models import BirthdayProduct
        from foods.models import FoodsProduct
        from fruitsandvegetables.models import FavProduct
        from gifts.models import GiftsProduct
        from pharmacy.models import PharmacyProduct
        from phones.models import PhonesProduct
        from products.models import LibraryProduct
        from shein.models import SheinProduct
        from socks.models import SocksProduct
        from spices.models import SpicesProduct
        from supermarket.models import SupermarketProduct
        from toys.models import ToysProduct
        from veils.models import VeilsProduct
        PRODUCT_MODELS = {
            'Shein': SheinProduct, 'Foods': FoodsProduct, 'Fav': FavProduct,
            'Pharmacy': PharmacyProduct, 'Phones': PhonesProduct, 'Spices': SpicesProduct,
            'Supermarket': SupermarketProduct, 'Toys': ToysProduct, 'Veils': VeilsProduct,
            'Socks': SocksProduct, 'Birthday': BirthdayProduct, 'Gifts': GiftsProduct,
            'Accessories': AccessoriesProduct, 'Library': LibraryProduct,
        }
    return PRODUCT_MODELS


def _stars(value):
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return None
    if 1 <= rating <= 5:
        return rating
    return None


def _display_name(user):
    name = (user.get_full_name() or '').strip() or user.first_name or user.username
    return name or 'عميل'


def _bought(user, model, product_id):
    if not user.is_authenticated:
        return False
    content_type = ContentType.objects.get_for_model(model)
    return OrderItem.objects.filter(
        order__user=user,
        content_type=content_type,
        object_id=product_id,
    ).exists()


@api_view(['GET'])
@permission_classes([AllowAny])
def product_reviews(request):
    model_name = request.GET.get('model_name', '')
    model = _models().get(model_name)
    try:
        product_id = int(request.GET.get('product_id', ''))
    except (TypeError, ValueError):
        product_id = None
    if model is None or product_id is None or not model.objects.filter(id=product_id).exists():
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    reviews = ProductReview.objects.filter(
        model_name=model_name,
        product_id=product_id,
    ).select_related('user').order_by('-created_at')
    summary = reviews.aggregate(average=Avg('rating'), count=Count('id'))
    distribution = {str(star): 0 for star in range(1, 6)}
    for row in reviews.values('rating').annotate(total=Count('id')):
        distribution[str(row['rating'])] = row['total']

    mine = None
    if request.user.is_authenticated:
        own = reviews.filter(user=request.user).first()
        if own is not None:
            mine = {'rating': own.rating, 'comment': own.comment}

    return Response({
        'average': round(float(summary['average'] or 0), 1),
        'count': summary['count'] or 0,
        'distribution': distribution,
        'can_review': request.user.is_authenticated,
        'verified_purchase': _bought(request.user, model, product_id),
        'mine': mine,
        'results': [
            {
                'id': review.id,
                'user_name': _display_name(review.user),
                'rating': review.rating,
                'comment': review.comment,
                'verified_purchase': review.verified_purchase,
                'created_at': review.created_at.isoformat(),
                'mine': request.user.is_authenticated and review.user_id == request.user.id,
            }
            for review in reviews[:30]
        ],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_product(request):
    model_name = request.data.get('model_name', '')
    model = _models().get(model_name)
    rating = _stars(request.data.get('rating'))
    comment = str(request.data.get('comment', '')).strip()[:500]
    try:
        product_id = int(request.data.get('product_id'))
    except (TypeError, ValueError):
        product_id = None
    if model is None or product_id is None or rating is None:
        return Response({'error': 'A product and a rating from 1 to 5 are required'}, status=400)
    if not model.objects.filter(id=product_id).exists():
        return Response({'error': 'Product not found'}, status=404)

    review, _ = ProductReview.objects.update_or_create(
        user=request.user,
        model_name=model_name,
        product_id=product_id,
        defaults={
            'rating': rating,
            'comment': comment,
            'verified_purchase': _bought(request.user, model, product_id),
        },
    )
    return Response({'id': review.id, 'rating': review.rating})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_app(request):
    rating = _stars(request.data.get('rating'))
    suggestion = str(request.data.get('suggestion', '')).strip()[:800]
    if rating is None:
        return Response({'error': 'Choose a rating from 1 to 5'}, status=400)

    order = None
    order_id = request.data.get('order_id')
    if order_id not in (None, ''):
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if order is None:
            return Response({'error': 'Order not found'}, status=404)
        feedback, _ = AppFeedback.objects.update_or_create(
            user=request.user,
            order=order,
            defaults={'rating': rating, 'suggestion': suggestion},
        )
    else:
        feedback = AppFeedback.objects.create(
            user=request.user,
            rating=rating,
            suggestion=suggestion,
        )
    return Response({'id': feedback.id, 'rating': feedback.rating})


@api_view(['POST'])
@permission_classes([AllowAny])
def card_ratings(request):
    items = request.data.get('items') or []
    pairs = []
    allowed = _models()
    for item in items[:200]:
        if not isinstance(item, dict):
            continue
        model_name = str(item.get('model_name', ''))
        try:
            product_id = int(item.get('product_id'))
        except (TypeError, ValueError):
            continue
        if model_name in allowed:
            pairs.append((model_name, product_id))
    if not pairs:
        return Response({})

    query = Q()
    for model_name, product_id in pairs:
        query |= Q(model_name=model_name, product_id=product_id)
    rows = (
        ProductReview.objects.filter(query)
        .values('model_name', 'product_id')
        .annotate(average=Avg('rating'), count=Count('id'))
    )
    payload = {
        f"{row['model_name']}:{row['product_id']}": {
            'average': round(float(row['average'] or 0), 1),
            'count': row['count'],
        }
        for row in rows
    }
    return Response(payload)

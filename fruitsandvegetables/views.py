from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .filters import ProductsFilter
from .models import FavProduct, FavReview
from .serializers import ProductSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg

@api_view(['GET'])
def get_all_products(request):
    # التحقق مما إذا كان المستخدم يريد عرض جميع المنتجات
    show_all = request.GET.get('all', 'false').lower() == 'true'

    queryset = FavProduct.objects.filter(is_active=True)

    # تطبيق الفلاتر على جميع المنتجات
    filterset = ProductsFilter(request.GET, queryset=queryset.order_by('id'))
    queryset = filterset.qs
    count = queryset.count()  # إجمالي عدد المنتجات

    if not show_all:
        # تطبيق Pagination إذا لم يتم طلب جميع المنتجات
        resPage = 12
        paginator = PageNumberPagination()
        paginator.page_size = resPage
        queryset = paginator.paginate_queryset(queryset, request)

    # تسلسل البيانات
    serializer = ProductSerializer(queryset, many=True, context={'request': request})

    # إرجاع النتائج
    return Response({
        "products": serializer.data,
        "count": count,
        "all": show_all
    })

@api_view(['GET'])
def get_by_id_product(request, pk):
    product = get_object_or_404(FavProduct, id=pk)
    serializer = ProductSerializer(product, many=False, context={'request': request})
    return Response({"product": serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def new_product(request):
    data = request.data
    serializer = ProductSerializer(data=data)

    if serializer.is_valid():
        product = FavProduct.objects.create(
            name=data['name'],
            price=data['price'],
            model_name=data['model_name'],
            primary_image=request.FILES.get('primary_image', None),
            secondary_image1=request.FILES.get('secondary_image1', None),
            secondary_image2=request.FILES.get('secondary_image2', None),
            description=data.get('description', ''),
            stock=data['stock'],
            user=request.user,
            delivery_days=data.get('delivery_days', 1),
            is_active=data.get('is_active', True)
        )
        res = ProductSerializer(product, many=False, context={'request': request})
        return Response({"product": res.data})
    else:
        return Response(serializer.errors)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_product(request, pk):
    product = get_object_or_404(FavProduct, id=pk)

    if product.user != request.user:
        return Response({"error": "Sorry, you cannot update this product"},
                        status=status.HTTP_403_FORBIDDEN)

    data = request.data
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.model_name = data.get('model_name',product.model_name)
    product.primary_image = request.FILES.get('primary_image', product.primary_image)
    product.secondary_image1 = request.FILES.get('secondary_image1', product.secondary_image1)
    product.secondary_image2 = request.FILES.get('secondary_image2', product.secondary_image2)
    product.description = data.get('description', product.description)
    product.stock = data.get('stock', product.stock)
    product.delivery_days = data.get('delivery_days', product.delivery_days)
    is_active_str = str(data.get('is_active', product.is_active)).lower()
    product.is_active = is_active_str == 'true'

    product.save()
    serializer = ProductSerializer(product, many=False, context={'request': request})
    return Response({"product": serializer.data})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_product(request, pk):
    product = get_object_or_404(FavProduct, id=pk)

    if product.user != request.user:
        return Response({"error": "Sorry, you cannot delete this product"},
                        status=status.HTTP_403_FORBIDDEN)

    product.delete()
    return Response({"details": "Delete action is done"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    product = get_object_or_404(FavProduct, id=pk)
    data = request.data
    review = product.reviews.filter(user=user)

    if data['rating'] <= 0 or data['rating'] > 10:
        return Response({"error": "Please select a rating between 1 to 10 only"},
                        status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review = {'rating': data['rating'], 'comment': data['comment']}
        review.update(**new_review)

        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()

        return Response({'details': 'Product review updated'})
    else:
        FavReview.objects.create(
            user=user,
            product=product,
            rating=data['rating'],
            comment=data['comment']
        )
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()
        return Response({'details': 'Product review created'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    product = get_object_or_404(FavProduct, id=pk)
    review = product.reviews.filter(user=user)

    if review.exists():
        review.delete()
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0
        product.ratings = rating['avg_ratings']
        product.save()
        return Response({'details': 'Product review deleted'})
    else:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from .models import Category
from .serializers import CategorySerializer
from rest_framework.permissions import AllowAny

# API لإرجاع جميع الفئات
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True, context={'request': request})
    return Response(serializer.data)

# API لإرجاع فئة معينة باستخدام ID
@api_view(['GET'])
@permission_classes([AllowAny])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=404)

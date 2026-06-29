from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .filters import ProductsFilter
from .models import PharmacyProduct, PharmacyReview
from .serializers import ProductSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg , Count
from django.contrib.contenttypes.models import ContentType
from allproducts.models import ProductVariant
import json

@api_view(['GET'])
def get_all_products(request):
    # التحقق مما إذا كان المستخدم يريد عرض جميع المنتجات
    show_all = request.GET.get('all', 'false').lower() == 'true'

    # 1. جلب المنتجات النشطة بدون ترتيب عشوائي لضمان سرعة الفلترة والعد
    queryset = PharmacyProduct.objects.filter(is_active=True)\
        .prefetch_related('variants')\
        .order_by('?')

    # تطبيق الفلاتر على المنتجات
    filterset = ProductsFilter(request.GET, queryset=queryset)
    queryset = filterset.qs
    
    # حساب العدد الإجمالي للمنتجات المفلترة بسرعة
    count = queryset.count()  

    if not show_all:
        # تطبيق Pagination إذا لم يتم طلب جميع المنتجات
        resPage = 12
        paginator = PageNumberPagination()
        paginator.page_size = resPage
        queryset = paginator.paginate_queryset(queryset, request)

    # تسلسل البيانات وتحويلها لـ JSON
    serializer = ProductSerializer(queryset, many=True, context={'request': request})

    # إرجاع النتائج
    return Response({
        "products": serializer.data,
        "count": count,
        "all": show_all
    })

@api_view(['GET'])
def get_by_id_product(request, pk):
    product = get_object_or_404(PharmacyProduct.objects.prefetch_related('variants'), id=pk)
    serializer = ProductSerializer(product, many=False, context={'request': request})
    return Response({"product": serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def new_product(request):
    data = request.data
    serializer = ProductSerializer(data=data)

    if serializer.is_valid():
        product = PharmacyProduct.objects.create(
            name=data['name'],
            original_price=data['original_price'],
            discount_percentage=data['discount_percentage'],
            model_name=data['model_name'],
            primary_image=request.FILES.get('primary_image', None),
            secondary_image1=request.FILES.get('secondary_image1', None),
            secondary_image2=request.FILES.get('secondary_image2', None),
            description=data.get('description', ''),
            stock=data['stock'],
            user=request.user,
            delivery_days=data.get('delivery_days', 1),
            is_active=data.get('is_active', True),
            is_available=data.get('is_available', True)
        )
        product.save()
        # --- الجزء الخاص برفع الألوان عبر الـ API عند إنشاء منتج جديد ---
        variants_data = request.data.get('variants_json') 
        if variants_data:
            try:
                variants_list = json.loads(variants_data)
                content_type = ContentType.objects.get_for_model(PharmacyProduct)
                
                # استخدام enumerate للحصول على الـ index لالتقاط الملفات بشكل ديناميكي
                for index, v_data in enumerate(variants_list):
                    ProductVariant.objects.create(
                        content_type=content_type,
                        object_id=product.id,
                        color_name=v_data.get('color_name'),
                        color_code=v_data.get('color_code'),
                        size=v_data.get('size'),
                        original_price=v_data.get('original_price', product.original_price),
                        discount_percentage=v_data.get('discount_percentage', product.discount_percentage),
                        stock=v_data.get('stock', 0),
                        is_active=v_data.get('is_active', True),
                        # التقاط ملفات الصور من request.FILES بناءً على الـ index
                        variant_image1=request.FILES.get(f'variant_{index}_image1'),
                        variant_image2=request.FILES.get(f'variant_{index}_image2'),
                        variant_image3=request.FILES.get(f'variant_{index}_image3'),
                    )
            except Exception as e:
                pass


        res = ProductSerializer(product, many=False, context={'request': request})
        return Response({"product": res.data})
    else:
        return Response(serializer.errors)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_product(request, pk):
    product = get_object_or_404(PharmacyProduct, id=pk)

    if product.user != request.user:
        return Response({"error": "Sorry, you cannot update this product"},
                        status=status.HTTP_403_FORBIDDEN)

    data = request.data
    product.name = data.get('name', product.name)
    product.original_price = data.get('original_price', product.original_price)
    product.discount_percentage = data.get('discount_percentage', product.discount_percentage)
    product.model_name = data.get('model_name',product.model_name)
    product.primary_image = request.FILES.get('primary_image', product.primary_image)
    product.secondary_image1 = request.FILES.get('secondary_image1', product.secondary_image1)
    product.secondary_image2 = request.FILES.get('secondary_image2', product.secondary_image2)
    product.description = data.get('description', product.description)
    product.stock = data.get('stock', product.stock)
    product.delivery_days = data.get('delivery_days', product.delivery_days)

    is_active_str = str(data.get('is_active', product.is_active)).lower()
    product.is_active = is_active_str == 'true'

    is_available_str = str(data.get('is_available', product.is_available)).lower()
    product.is_available = is_available_str == 'true'

    product.save()
    # 2. تحديث إدارة المتغيرات (الألوان والمقاسات والصور)
    variants_data = request.data.get('variants_json')
    if variants_data:
        try:
            variants_list = json.loads(variants_data)
            content_type = ContentType.objects.get_for_model(PharmacyProduct)
            
            # مصفوفة لحفظ الـ IDs الخاصة بالمتغيرات التي نريد الإبقاء عليها
            keep_variant_ids = []
            
            for index, v_data in enumerate(variants_list):
                variant_id = v_data.get('id')  # لو المتغير موجود من قبل، الفرونت هيبعت الـ id بتاعه
                
                # تجهيز الحقول النصية والرقمية للمتغير
                variant_fields = {
                    'color_name': v_data.get('color_name'),
                    'color_code': v_data.get('color_code'),
                    'size': v_data.get('size'),
                    'original_price': v_data.get('original_price', product.original_price),
                    'discount_percentage': v_data.get('discount_percentage', product.discount_percentage),
                    'stock': v_data.get('stock', 0),
                }
                
                # التقاط الصور الجديدة الديناميكية إذا تم رفعها من الفرونت
                # الفرونت إند (Flutter) هيبعتها في الـ FILES بـ Keys واضحة مثل: variant_0_image1
                img1 = request.FILES.get(f'variant_{index}_image1')
                img2 = request.FILES.get(f'variant_{index}_image2')
                img3 = request.FILES.get(f'variant_{index}_image3')
                
                if img1: variant_fields['variant_image1'] = img1
                if img2: variant_fields['variant_image2'] = img2
                if img3: variant_fields['variant_image3'] = img3

                if variant_id:
                    # [تعديل] المتغير موجود بالفعل في قاعدة البيانات
                    variant = ProductVariant.objects.filter(id=variant_id, content_type=content_type, object_id=product.id).first()
                    if variant:
                        for attr, value in variant_fields.items():
                            setattr(variant, attr, value)
                        variant.save()
                        keep_variant_ids.append(variant.id)
                else:
                    # [إنشاء] متغير جديد تماماً تم إضافته أثناء التعديل
                    new_variant = ProductVariant.objects.create(
                        content_type=content_type,
                        object_id=product.id,
                        **variant_fields
                    )
                    keep_variant_ids.append(new_variant.id)
            
            # [حذف] أي متغيرات قديمة لم تعد موجودة في القائمة القادمة من الفرونت إند
            product.variants.exclude(id__in=keep_variant_ids).delete()

        except Exception as e:
            # يمكنك طباعة الخطأ لمعرفته أثناء التستنج: print(e)
            pass
    serializer = ProductSerializer(product, many=False, context={'request': request})
    return Response({"product": serializer.data})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_product(request, pk):
    product = get_object_or_404(PharmacyProduct, id=pk)

    if product.user != request.user:
        return Response({"error": "Sorry, you cannot delete this product"},
                        status=status.HTTP_403_FORBIDDEN)

    product.delete()
    return Response({"details": "Delete action is done"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    product = get_object_or_404(PharmacyProduct, id=pk)
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
        PharmacyReview.objects.create(
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
    product = get_object_or_404(PharmacyProduct, id=pk)
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

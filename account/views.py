from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render 
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import SignUpSerializer , UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from random import randint 
from django.conf import settings
from .models import Profile
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    user = SignUpSerializer(data=data)

    if user.is_valid():
        # التحقق من صحة عنوان البريد الإلكتروني
        try:
            validate_email(data['email'])
        except ValidationError as e:
            return Response({'error': 'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من عدم وجود بريد إلكتروني مكرر
        if not User.objects.filter(username=data['email']).exists():
            user = User.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                username=data['email'],
                password=make_password(data['password']),
            )
            return Response({'details': 'Your account registered successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'This email already exists!'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = UserSerializer(request.user, many = False)
    print(user.data)
    return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data
    
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.email = data['email']
    user.user_name = data['email']

    if data['password'] != "":
        user.password = make_password(data['password'])

    user.save()
    serializer = UserSerializer(user, many = False)
    return Response(serializer.data)


def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol = protocol, host = host)


from django.utils import timezone  # 👈 استيراد مكتبة الوقت المتوافقة مع دجانجو

from django.utils import timezone  # 🚀 تأكد من وجود هذا الاستيراد في الأعلى

# 1️⃣ دالة forgot_password
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User, email=data['email'])
    
    profile, created = Profile.objects.get_or_create(user=user)
    
    token = str(randint(1000, 9999))
    
    # 🎯 الحساب الصحيح المتوافق مع دجانجو والـ Timezone بدون أي تحذيرات
    expire_date = timezone.now() + timedelta(minutes=30)
    
    profile.reset_password_token = token
    profile.reset_password_expire = expire_date
    profile.save()
    
    subject = "Password Reset Code - Aswaq Mozhela"
    body = f"Hello,\n\nYour 4-digit verification code to reset your password is: {token}\n\nThis code will expire in 30 minutes."
    
    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [data['email']],
        fail_silently=False,
    )
    
    return Response({'details': 'Password reset code sent successfully.'})


# 2️⃣ دالة verify_reset_token
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_token(request, token):
    user = get_object_or_404(User, profile__reset_password_token=token)

    # 🔬 سطر الـ Debug للتأكيد (هتلاقيهم دلوقتى متطابقين في نفس النطاق الزمني)
    print(f"⏰ وقت السيرفر الحالي (Aware): {timezone.now()}")
    print(f"💾 وقت انتهاء الكود في الداتابيز (Aware): {user.profile.reset_password_expire}")

    # 🎯 المقارنة الشرعية الصحيحة بين وقتين يدعموا الـ Timezone
    if user.profile.reset_password_expire < timezone.now():
        return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)
   
    return Response({'message': 'Token is valid.'}, status=200)
 

# 3️⃣ دالة reset_password
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, token):
    data = request.data
    # جلب المستخدم المرتبط بهذا الـ token من خلال البروفايل
    user = get_object_or_404(User, profile__reset_password_token=token)

    # التحقق من صلاحية الوقت
    if user.profile.reset_password_expire < timezone.now():
        return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    # التحقق من تطابق حيلين كلمة المرور
    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 🚀 الحل السحري: استخدام set_password بدلاً من make_password يدوياً
    user.set_password(data['password'])
    user.save()  # حفظ المستخدم أولاً بالباسورد المشفر الجديد
    
    # تصوير وتصفير بيانات التوكن في البروفايل عشان مايستخدمش تاني
    profile = user.profile
    profile.reset_password_token = ""
    profile.reset_password_expire = None
    profile.save()
    
    return Response({'details': 'Password reset successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_phone_number(request):
    phone_number = "01557813252"  # رقم الهاتف الذي تريد الاتصال به
    return Response({'phone_number': phone_number})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_delivery_Cost(request):
    delivery_Cost = "35" 
    return Response({'delivery_Cost': delivery_Cost})




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        # تحديث حالة تسجيل الخروج للمستخدم
        user = request.user
        user.is_logged_out = True
        user.save()

        # تسجيل الخروج
        logout(request)

        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    try:
        user = request.user
        user.delete()

        return Response({'message': 'User account deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_type(request):
    user = request.user
    if user.is_superuser:
        return JsonResponse({'user_type': 'admin'})
    elif user.is_staff:
        return JsonResponse({'user_type': 'staff'})
    else:
        return JsonResponse({'user_type': 'user'})
    

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    data = request.data
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    # تحقق إذا كان المستخدم موجود
    user = User.objects.filter(email=email).first()

    if user is None:
        # في حال كان المستخدم غير موجود، نقوم بإنشاء مستخدم جديد
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
        )
        user.save()

    # تحقق من وجود بروفايل للمستخدم، إذا لم يكن موجودًا، قم بإنشائه
    if not hasattr(user, 'profile'):
        profile = Profile.objects.create(user=user)
        profile.save()

    # تحديد نوع المستخدم (admin, staff, user)
    if user.is_superuser:
        user_type = 'admin'
    elif user.is_staff:
        user_type = 'staff'
    else:
        user_type = 'user'

    # الآن بعد التحقق من وجود المستخدم، يمكننا إصدار Token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # إرسال ID Token للمستخدم مع user_type
    return Response({
        'access_token': access_token,
        'user_type': user_type  # إضافة نوع المستخدم في الاستجابة
    })

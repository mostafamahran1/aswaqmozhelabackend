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


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User,email = data['email'])
    token = str(randint(1000, 9999))
    expire_date = datetime.now() + timedelta(minutes=30)
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date
    user.profile.save()
    
    host = get_current_host(request)
    link = "{host}api/reset_password/{token}".format(host=host, token=token)
    body = "Your password reset link is: {link}".format(link=link)
    send_mail(
        "Password reset from aswaqmozhela",
        body,
        settings.EMAIL_HOST_USER,  # Sender's email address
        [data['email']],  # Recipient's email address
        fail_silently=False,  # Raise exception on failure
    )
    return Response({'details':'Password reset sent to {email}'.format(email = data['email'])})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_token(request, token):
    user = get_object_or_404(User,profile__reset_password_token = token)

    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error':'Token is expired'},status=status.HTTP_400_BAD_REQUEST)
   
    return Response({'message': 'Token is valid.'}, status=200)
 


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request,token):
    data = request.data
    user = get_object_or_404(User,profile__reset_password_token = token)

    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error':'Token is expired'},status=status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error':'Password are not same'},status=status.HTTP_400_BAD_REQUEST)
    
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None
    user.profile.save()
    user.save()
    return Response({'details':'Password reset successfully'})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_phone_number(request):
    phone_number = "01009345616"  # رقم الهاتف الذي تريد الاتصال به
    return Response({'phone_number': phone_number})




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
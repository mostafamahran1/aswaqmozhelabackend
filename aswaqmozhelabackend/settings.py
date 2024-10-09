"""
Django settings for aswaqmozhelabackend project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+_uhbip6ikra2&!&mnoq(1w6g1p4%ja)ds+mw@%3jgf-_nn5p0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*','54.159.170.230', 'localhost', '127.0.0.1', '10.0.2.2']


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'allproducts.apps.AllproductsConfig',
    'supermarket.apps.SupermarketConfig',
    'spices.apps.SpicesConfig',
    'pharmacy.apps.PharmacyConfig',
    'fruitsandvegetables.apps.FruitsandvegetablesConfig',
    'foods.apps.FoodsConfig',
    'clothes.apps.ClothesConfig',
    'phones.apps.PhonesConfig',
    'toys.apps.ToysConfig',
    'order.apps.OrderConfig',
    'account.apps.AccountConfig',
    'products.apps.ProductsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'mahranmostafa900@gmail.com'
EMAIL_HOST_PASSWORD = 'qjxs kjhm tfme wdrn'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

ROOT_URLCONF = 'aswaqmozhelabackend.urls'
CORS_ALLOW_ALL_ORIGINS = True


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aswaqmozhelabackend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

#DATABASES = {
#     'default': {
#     'ENGINE' : 'django.db.backends.postgresql_psycopg2',
#     'NAME' : 'do267h46ng04q',
#     'USER' : 'u400t3099h9dbc',
#     'PASSWORD' : 'p1b4197dfb9df703770c7eb35ccf91bb0042df369f499304a65129be33ec8e785',
#     'HOST' : 'c1i13pt05ja4ag.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',
#     'PORT' : '5432',
#   }
#}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Ensure you have STATIC_ROOT defined
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional static file settings
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Cairo'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


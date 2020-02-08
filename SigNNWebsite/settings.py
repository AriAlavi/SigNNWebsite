"""
Django settings for SigNNWebsite project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import json
from django.core.management.utils import get_random_secret_key


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_FILE_PATH = os.path.join(BASE_DIR, "secret_info.json")
try:
    SECRET_FILE = open(SECRET_FILE_PATH, "r+")
    SECRET_DATA = json.load(SECRET_FILE)
except FileNotFoundError:
    SECRET_FILE = open(SECRET_FILE_PATH, "w+")
    SECRET_DATA = {}
except PermissionError:
    SECRET_FILE = None
    SECRET_DATA = {}


try:
    SECRET_KEY = SECRET_DATA["SECRET_KEY"]
except:
    SECRET_KEY = get_random_secret_key()
    SECRET_DATA["SECRET_KEY"] = SECRET_KEY

# .apps.googleusercontent.com.json should be last chars of GOOGLE_SECRETS file
GOOGLE_SECRETS_BROKEN_WHY = "Not detected"
try:
    GOOGLE_SECRETS = os.path.join(BASE_DIR, SECRET_DATA["GOOGLE_SECRETS"])
except Exception as e:
    GOOGLE_SECRETS = None
    GOOGLE_SECRETS_BROKEN_WHY = str(e)
    if SECRET_FILE:
        print("WARNING: GOOGLE AUTH WILL NOT WORK", e)

try:
    MAIN_URL = SECRET_DATA["MAIN_URL"]
except:
    MAIN_URL = "localhost:8000"
    SECRET_DATA["MAIN_URL"] = MAIN_URL

try:
    HTTP_OR_HTTPS = SECRET_DATA["HTTP_OR_HTTPS"]
except:
    HTTP_OR_HTTPS = "http://"
    SECRET_DATA["HTTP_OR_HTTPS"] = HTTP_OR_HTTPS




# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', 'ec2-52-53-248-163.us-west-1.compute.amazonaws.com', "52.53.248.163", "www.signn.live"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig',
    'crispy_forms',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SigNNWebsite.urls'

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

WSGI_APPLICATION = 'SigNNWebsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases



try:
    DATABASE = (SECRET_DATA['database'])
except:
    DATABASE = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
    SECRET_DATA['database'] = DATABASE

if DATABASE['ENGINE'] == "django.db.backends.postgresql":
    import psycopg2.extensions

DATABASES = {
    'default' : DATABASE
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGIN_REDIRECT_URL = 'profile'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

if SECRET_FILE is not None:
    SECRET_FILE.close()
    SECRET_FILE = open(SECRET_FILE_PATH, "w+")
    json.dump(SECRET_DATA, SECRET_FILE,indent=2)
    SECRET_FILE.close()


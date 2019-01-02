"""Django settings for archaeography.nz.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/

"""

import os
import socket

# SECRETS

# These variables contain identifiers and passwords for the local
# database, and for email and ArchSite accounts. Obviously, we can't
# release our own, so this section provides dummy versions, which
# won't work.

SECRET_KEY = 'yyi16c3w@a6+)lcc%0pf9*0ys4wnvkl^clm0qi=65)^ww!p0s7'
MACHINE = ('django_superuser_id', 'some pass phrase')
LOGIN_ARCHSITE = {
    'default': ('archsite_userid', 'archsite password'),
    'username': ('archsite_userid', 'archsite password'),
    'seconduser': ('archsite_userid', 'archsite password'),
}
GMAIL = ('address@gmail.com', 'gmail password')
# end SECRETS

# Secret variables above are replaced by the following import
# statement. You should copy the code above into a separate file
# called 'secrets.py', and modify it appropriately. Otherwise, comment
# out the following line.
from secrets import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    'archaeography.nz', 'archaeography.co.nz',
    'archaeography',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.sites',

    'geolib',
    'home',
    'members',
    'nzaa',
]
SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'home.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'home.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'arch_normal',
        'USER': MACHINE[0],
        'PASSWORD': MACHINE[1],
        'HOST': 'localhost',
        'PORT': '',
    }
}

SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

# This was taken out because it was refusing to permit the creation of
# a superuser.
DEPRECIATED_AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.\
        UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.\
        MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.\
        CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.\
        NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-nz'

TIME_ZONE = 'NZ'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/archaeography/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = GMAIL[0]
EMAIL_HOST_PASSWORD = GMAIL[1]
EMAIL_PORT = 587
DEFAULT_EMAIL_FROM = "archaeographynz@gmail.com"

# Security settings

SECURE_CONTENT_TYPE_NOSNIF = True
SECURE_BROWSER_XSS_FILTER = True
SCURE_SSL_REDIRECT = False
# SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

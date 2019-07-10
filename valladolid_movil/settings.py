#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# ********** Environment Variables **********
from decouple import config

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)
#DEBUG = True

SITE_ID = 1

ALLOWED_HOSTS = [
    '*',
]

# ********** MAIL SERVER CONFIG **********

EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'valladolidmovil@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# ********** SESSION CONFIG **********

LOGIN_URL = 'cms:custom_login'
LOGOUT_REDIRECT_URL = 'cms:home'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'widget_tweaks',
    'rest_framework',
    'generic_relations',
    'embed_video',
    'ckeditor',
    #'django_filters',
    'storages',
    'cms',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'valladolid_movil.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
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

WSGI_APPLICATION = 'valladolid_movil.wsgi.application'


# ********** Database Config **********
from dj_database_url import parse as dburl
default_dburl = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = { 'default': config('DATABASE_URL', default=default_dburl, cast=dburl), }

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'es-ES'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# ********** STATIC FILES **********
# DEVELOPMENT
"""
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_FINDERS = [
   "django.contrib.staticfiles.finders.FileSystemFinder",
   "django.contrib.staticfiles.finders.AppDirectoriesFinder"
]
"""
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# ********** STATIC FILES **********
# Production

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_FINDERS = [
   "django.contrib.staticfiles.finders.FileSystemFinder",
   "django.contrib.staticfiles.finders.AppDirectoriesFinder"
]

#STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
#AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
#AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = 'bucketvalladolidcms'
#AWS_S3_OBJECT_PARAMETERS = { 'CacheControl': 'max-age=86400' }
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

AWS_DEFAULT_ACL = 'public-read'
#ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

DEFAULT_FILE_STORAGE = 'cms.files.MediaStorage'

STATIC_LOCATION = 'static'
STATICFILES_STORAGE = 'cms.files.StaticStorage'
STATIC_URL='https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, STATIC_LOCATION)

# ********** MEDIA FILES **********

# Development
"""
MEDIA_URL = '/media/'

MEDIAFILES_DIRS = [
    os.path.join(BASE_DIR, "media"),
]
"""
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Production

MEDIAFILES_DIRS = [
    os.path.join(BASE_DIR, "media"),
]

MEDIA_LOCATION = 'media'
MEDIAFILES_STORAGE = 'cms.files.MediaStorage'
MEDIA_URL='https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, MEDIA_LOCATION)
# ********** RESTFRAMEWORKS **********

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# ********** CORSEHEADERS *********

CORS_ORIGIN_ALLOW_ALL = True

# ********** BACKENDS **********

# Authentication Backends for Django and Admin
AUTHENTICATION_BACKENDS = [
    'cms.backend.CustomBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ********** CKEDITOR CONFIG **********

CKEDITOR_UPLOAD_PATH = 'ckeditor/'
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = False
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = 'pillow'

CKEDITOR_CONFIGS = {
    'full': {
        'toolbar': 'Full',
        'width': '100%',
        'extraPlugins': ','.join([

        ]),
        'allowedContent': True,
        'enterMode': 2,
    },
}




#


#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION
    default_acl = 'public-read'
    #file_overwrite = False


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIA_LOCATION
    default_acl = 'public-read'
    file_overwrite = False

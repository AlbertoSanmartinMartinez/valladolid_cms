#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static

from valladolid_movil import settings
from cms import urls as cms_urls
from cms import views as cms_views

admin.site.site_header = 'Valladolid Móvil CMS'
admin.autodiscover()


urlpatterns = [

    # Home
    path('', cms_views.home, name='base'),

    # Admin Urls
    path('admin/', admin.site.urls),

    # CMS Urls
    path('cms/', include((cms_urls, 'cms'), namespace='cms')),

    # Error Handler Urls
    #handler400 = 'cms_views.handler400'
    #handler403 = 'cms_views.handler403'
    #handler404 = 'cms_views.handler404'
    #handler500 = 'cms_views.handler500'

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#!/usr/local/bin/python
# -*- coding: utf-8 -*-


from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

from cms import views as cms_views


urlpatterns = [

    path('', cms_views.home, name='base'),
    path('inicio/', cms_views.home, name='home'),

    path('acceso/', cms_views.custom_login, name='custom_login'),
    path('desconectar/', auth_views.LogoutView.as_view(), name='logout'),

    path('activacion/<uidb64>/<token>/', cms_views.activation, name='activation'),
    path('password_reset/', cms_views.password_reset, name='password_reset'),
    path('password_reset_form/<uidb64>/<token>/', cms_views.password_reset_form, name='password_reset_form'),

    # reset password form

    # Categorias Urls
    path('categorias/', cms_views.category_list, name='category_list'),
    path('categorias/crear', cms_views.category_create, name='category_create'),
    path('categorias/filtrar', cms_views.category_filter, name='category_filter'),
    path('categorias/scrap', cms_views.category_scrap, name='category_scrap'),
    path('categorias/upload', cms_views.category_upload, name='category_upload'),
    path('categorias/<int:id>/editar', cms_views.category_update, name='category_update'),
    path('categorias/<int:id>/ver', cms_views.category_view, name='category_view'),
    path('categorias/<int:id>/borrar', cms_views.category_delete, name='category_delete'),

    # Lugares Urls
    path('lugares/', cms_views.place_list, name='place_list'),
    path('lugares/crear', cms_views.place_create, name='place_create'),
    path('lugares/filtrar', cms_views.place_filter, name='place_filter'),
    path('lugares/scrap', cms_views.place_scrap, name='place_scrap'),

    path('lugares/upload', cms_views.place_upload, name='place_upload'),
    path('lugares/<int:id>/editar', cms_views.place_update, name='place_update'),
    path('lugares/<int:id>/ver', cms_views.place_view, name='place_view'),
    path('lugares/<int:id>/borrar', cms_views.place_delete, name='place_delete'),

    # Promos Urls
    path('promociones/', cms_views.promo_list, name='promo_list'),
    path('promociones/crear', cms_views.promo_create, name='promo_create'),
    path('promociones/filtrar', cms_views.promo_filter, name='promo_filter'),
    path('promociones/scrap', cms_views.promo_scrap, name='promo_scrap'),

    path('promociones/upload', cms_views.promo_upload, name='promo_upload'),
    path('promociones/<int:id>/editar', cms_views.promo_update, name='promo_update'),
    path('promociones/<int:id>/ver', cms_views.promo_view, name='promo_view'),
    path('promociones/<int:id>/borrar', cms_views.promo_delete, name='promo_delete'),

    # Precios Urls
    path('precios/', cms_views.price_list, name='price_list'),
    path('precios/crear', cms_views.price_create, name='price_create'),
    path('precios/filtrar', cms_views.price_filter, name='price_filter'),
    path('precios/scrap', cms_views.price_scrap, name='price_scrap'),

    path('precios/upload', cms_views.price_upload, name='price_upload'),
    path('precios/<int:id>/editar', cms_views.price_update, name='price_update'),
    path('precios/<int:id>/ver', cms_views.price_view, name='price_view'),
    path('precios/<int:id>/borrar', cms_views.price_delete, name='price_delete'),

    # Horarios Urls
    path('horarios/', cms_views.schedule_list, name='schedule_list'),
    path('horarios/crear', cms_views.schedule_create, name='schedule_create'),
    path('horarios/filtrar', cms_views.schedule_filter, name='schedule_filter'),
    path('horarios/scrap', cms_views.schedule_scrap, name='schedule_scrap'),

    path('horarios/upload', cms_views.schedule_upload, name='schedule_upload'),
    path('horarios/<int:id>/editar', cms_views.schedule_update, name='schedule_update'),
    path('horarios/<int:id>/ver', cms_views.schedule_view, name='schedule_view'),
    path('horarios/<int:id>/borrar', cms_views.schedule_delete, name='schedule_delete'),

    # Publicaciones Urls
    path('publicaciones/', cms_views.publication_list, name='publication_list'),
    path('publicaciones/crear', cms_views.publication_create, name='publication_create'),
    path('publicaciones/filtrar', cms_views.publication_filter, name='publication_filter'),
    path('publicaciones/scrap', cms_views.publication_scrap, name='publication_scrap'),

    path('publicaciones/upload', cms_views.publication_upload, name='publication_upload'),
    path('publicaciones/<int:id>/editar', cms_views.publication_update, name='publication_update'),
    path('publicaciones/<int:id>/ver', cms_views.publication_view, name='publication_view'),
    path('publicaciones/<int:id>/borrar', cms_views.publication_delete, name='publication_delete'),

    # Usuarios Urls
    path('usuarios/', cms_views.user_list, name='user_list'),
    path('usuarios/crear', cms_views.user_create, name='user_create'),
    path('usuarios/filtrar', cms_views.user_filter, name='user_filter'),
    path('usuarios/scrap', cms_views.user_scrap, name='user_scrap'),

    path('usuarios/upload', cms_views.user_upload, name='user_upload'),
    path('usuarios/<int:id>/editar', cms_views.user_update, name='user_update'),
    path('usuarios/<int:id>/ver', cms_views.user_view, name='user_view'),
    path('usuarios/<int:id>/borrar', cms_views.user_delete, name='user_delete'),

    # Imagenes Urls
    path('imagenes/', cms_views.image_list, name='image_list'),
    path('imagenes/crear', cms_views.image_create, name='image_create'),
    path('imagenes/filtrar', cms_views.image_filter, name='image_filter'),
    path('imagenes/scrap', cms_views.image_scrap, name='image_scrap'),

    path('imagenes/upload', cms_views.image_upload, name='image_upload'),
    path('imagenes/<int:id>/editar', cms_views.image_update, name='image_update'),
    path('imagenes/<int:id>/ver', cms_views.image_view, name='image_view'),
    path('imagenes/<int:id>/borrar', cms_views.image_delete, name='image_delete'),

    # Video Urls
    path('videos/', cms_views.video_list, name='video_list'),
    path('videos/crear', cms_views.video_create, name='video_create'),
    path('videos/filtrar', cms_views.video_filter, name='video_filter'),
    path('videos/scrap', cms_views.video_scrap, name='video_scrap'),

    path('videos/upload', cms_views.video_upload, name='video_upload'),
    path('videos/<int:id>/editar', cms_views.video_update, name='video_update'),
    path('videos/<int:id>/ver', cms_views.video_view, name='video_view'),
    path('videos/<int:id>/borrar', cms_views.video_delete, name='video_delete'),

    # Category API Urls
    path('rest_category_list/', cms_views.rest_category_list, name='rest_category_list'),
    path('rest_category_detail/', cms_views.rest_category_detail, name='rest_category_detail'),
    path('rest_category_final/', cms_views.rest_category_final, name='rest_category_final'),

    # Places API Urls
    #path('rest_places/<int:id>', cms_views.rest_place_list, name='rest_place_list'),
    path('rest_places/', cms_views.rest_place_list, name='rest_place_list'),

    # Places API Urls
    #path('rest_promos/<int:id>', cms_views.rest_promo_list, name='rest_promo_list'),
    path('rest_promos/', cms_views.rest_promo_list, name='rest_proms_list'),

    # Events API Urls
    #path('rest_events/<int:id>', cms_views.rest_event_list, name='rest_event_list'),
    path('rest_events/', cms_views.rest_event_list, name='rest_event_list'),

    # News API Urls
    #path('rest_news/<int:id>', cms_views.rest_new_list, name='rest_new_list'),
    path('rest_news/', cms_views.rest_new_list, name='rest_new_list'),

]




#


#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib

#from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait, Select

from django import forms

from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from valladolid_movil import settings
from cms import models as cms_models
from cms import forms as cms_forms
from cms import serializers as cms_serializers
from cms.tokens import account_activation_token


# General Views
def home(request):
    """
    """

    return render(request, 'home.html', {})


def custom_login(request):
    """
    """

    print("login function")

    title = 'Acceso'
    if request.method == 'POST':
        form = cms_forms.LoginForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)

                    return redirect('cms:category_list')
        else:
            print(form.errors)

    else:
        form = cms_forms.LoginForm()

    return render(request, 'login.html', {
        'title': title,
        'form': form,
    })


def activation(request, uidb64, token):
    """
    """

    print("activation function")

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(user)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        print("exception")
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        print("user is not None")
        user.is_active = True
        user.save()

        return redirect('cms:custom_login')

    else:
        print("user is None")
        print('Activation link is invalid!')
        return redirect('cms:home')


def password_reset(request):
    """
    """

    print("password reset function")

    if request.method == 'POST':
        print("post")

        form = cms_forms.ResetForm(request.POST)
        if form.is_valid():
            print("valid form")
            data = form.cleaned_data
            print(data['username'])

            user = User.objects.get(
                Q(username=data['username']) |
                Q(email=data['username']))

            if user is not None:
                print("user exist")
                if user.is_active:
                    print("user active")

                    current_site = get_current_site(request)
                    subject = 'Restablecer contraseña - Valladolid CMS'
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [user.email,]
                    message = render_to_string('email_password_reset.txt', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    })
                    send_mail(subject, message, from_email, to_email, fail_silently=False,)

                else:
                    print("user not active")
            else:
                print("user not exist")
        else:
            print(form.errors)

        return redirect('cms:home')

    else:
        print("get")
        form = cms_forms.ResetForm()

    return render(request, 'password_reset.html', {
        'form': form,
    })


def password_reset_form(request, uidb64=None, token=None):
    """
    """

    print("passwrod reset form function")

    user = None

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(user)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        print("user not existe")
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'GET':
            print("get")
            form = cms_forms.ResetPasswordForm(initial={'username': user.username})

    else:
        if request.method == 'POST':
            print("post")

            form = cms_forms.ResetPasswordForm(request.POST)
            if form.is_valid():
                print("valid form")
                data = form.cleaned_data
                user = User.objects.get(username=data['username'])

                if data['password1'] == data['password2']:
                    print(data['password1'])
                    user.set_password(data['password1'])
                    user.save()

                current_site = get_current_site(request)
                subject = 'Confirmación - Valladolid CMS'
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email,]
                message = render_to_string('email_activation.txt', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                send_mail(subject, message, from_email, to_email, fail_silently=False,)

                return redirect('cms:home')

            else:
                print(form.errors)

    print(user)

    return render(request, 'password_reset_form.html', {
        'form': form,
    })


# Category Views
@login_required()
def category_list(request, filter_dict=None):
    """
    list category view
    pagination function
    order function asc and desc for each attribute
    filter fields depends on user permissions
    urls route by model
    """

    print("category list function")

    title = 'Categorías'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = category_filter_2(filter_dict)

    else:
        elements = cms_models.Categoria.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = []
    exclude = ['en_titulo', 'subtitulo', 'en_subtitulo', 'en_informacion', 'informacion']
    [fields.append(field) for field in cms_models.Categoria._meta.fields if field.name not in exclude]

    urls = getCategoryUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)

    page = request.GET.get('page')
    if page is None:
        page = 1

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def category_create(request):
    """
    """

    print("category create function")

    title = 'Nueva Categoría'
    urls = getCategoryUrls()

    if request.method == 'POST':
        form = cms_forms.CategoryForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('cms:category_list')
    else:
        form = cms_forms.CategoryForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def category_update(request, id=None):
    """
    """

    print("category update function")

    title = 'Editar Categoría'
    element = get_object_or_404(cms_models.Categoria, id=id)
    urls = getCategoryUrls()

    if request.method == 'POST':
        form = cms_forms.CategoryForm(request.POST, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:category_list')
    else:
        form = cms_forms.CategoryForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def category_view(request, id=None):
    """
    """

    print("category view function")

    title = 'Ver Categoría'
    element = get_object_or_404(cms_models.Categoria, id=id)

    content_type = get_object_or_404(ContentType, model='categoria')
    images = cms_models.Imagen.objects.filter(content_type_id=content_type.id, object_id=id)
    videos = cms_models.Video.objects.filter(content_type_id=content_type.id, object_id=id)

    fields = []
    model_fields = cms_models.Categoria._meta.get_fields()
    print(model_fields)
    exclude_fields = []
    [fields.append(field) for field in model_fields if field.name not in exclude_fields]

    list = {}
    for field in element._meta.fields:
        attribute_class_name = field.__class__.__name__
        if attribute_class_name == 'ManyToManyField':
            pass
        elif attribute_class_name == 'ManyToOneRel':
            pass
        elif attribute_class_name == 'ForeignKey':
            #list['Subcategorías'] = element.parent_category.all()
            list[field.verbose_name] = getattr(element, field.name)
        else:
            list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
        'images': images,
        'videos': videos
    })


@login_required()
def category_delete(request, id=None):
    """
    """

    print("category delete function")

    title = 'Borrar Categoría'
    element = get_object_or_404(cms_models.Categoria, id=id)
    urls = getCategoryUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:category_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def category_filter(request):
    """
    """

    print("category filter function")

    title = 'Filtrar Categorías'
    urls = getCategoryUrls()

    if request.method == 'POST':
        print("POST")
        filter_dict = {}
        form = cms_forms.CategoryFilterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data['status'] is not None:
                filter_dict['status'] = data['status']

            if data['text'] is not None:
                filter_dict['text'] = data['text']

            if data['start_date'] is not None:
                filter_dict['start_date'] = data['start_date']

            if data['end_date'] is not None:
                filter_dict['end_date'] = data['end_date']

            if data['start_priority'] is not None:
                filter_dict['start_priority'] = data['start_priority']

            if data['end_priority'] is not None:
                filter_dict['end_priority'] = data['end_priority']

            if data['categoria_padre'] is not None:
                filter_dict['categoria_padre'] = data['categoria_padre']

            return category_list(request, filter_dict)

        else:
            print("form invalid")

    else:
        print("GET")
        form = cms_forms.CategoryFilterForm()

    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
    })


def category_filter_2(filter_dict):
    """
    """

    print("category filter 2 function")

    elements = cms_models.Categoria.objects.all()

    if filter_dict.get('status') is not None:
        elements = elements.filter(
        Q(estado=filter_dict['status']))

    if filter_dict.get('text') is not None:
        elements = elements.filter(
            Q(titulo__icontains=filter_dict["text"]) |
        Q(en_titulo__icontains=filter_dict["text"]) |
        Q(subtitulo__icontains=filter_dict["text"]) |
        Q(en_subtitulo__icontains=filter_dict["text"]) |
        Q(informacion__icontains=filter_dict["text"]) |
        Q(en_informacion__icontains=filter_dict["text"]))

    if filter_dict.get('start_date') is not None:
        elements = elements.filter(
        Q(created_date__gte=filter_dict['start_date']))

    if filter_dict.get('end_date') is not None:
        elements = elements.filter(
        Q(created_date__lte=filter_dict['end_date']))

    if filter_dict.get('start_priority') is not None:
        elements = elements.filter(
        Q(prioridad__gte=filter_dict['start_priority']))

    if filter_dict.get('end_priority') is not None:
        elements = elements.filter(
        Q(prioridad__lte=filter_dict['end_priority']))

    if filter_dict.get('categoria_padre') is not None:
        categoria_padre = get_object_or_404(cms_models.Categoria, titulo=filter_dict['categoria_padre'])
        elements = elements.filter(categoria_padre_id=categoria_padre.id)

    return elements


@login_required()
def category_scrap(request):
    """
    scrap with selenium all categories and subcategories
    """

    print("category scrap function")

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path='/Users/albertosanmartinmartinez/Downloads/chromedriver', chrome_options=option)
    browser.get('http://salamantica.com/cms/login')

    timeout = 5

    WebDriverWait(browser, timeout)

    browser.find_element_by_id("UserUsername").send_keys("rubenmartin@salamancamovil.com")
    browser.find_element_by_id("UserPassword").send_keys("D*JT3T6QDRkYc))TflBn)CH&")
    browser.find_element_by_css_selector('button[type="submit"]').click()

    WebDriverWait(browser, timeout)

    file = open("fixtures/categorias.txt","w")
    category_web = 'http://salamantica.com/cms/categories/view/'

    for i in range(1, 28):
        list = []

        browser.get(category_web + str(i))
        WebDriverWait(browser, timeout)
        information = browser.find_elements_by_class_name('controls')
        [ list.append(content.text) for content in information ]
        print(list)
        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    file = open("fixtures/subcategorias.txt","w")
    category_web = 'http://salamantica.com/cms/subcategories/view/'

    for i in range(1, 165):
        list = []

        browser.get(category_web + str(i))
        WebDriverWait(browser, timeout)
        information = browser.find_elements_by_class_name('controls')
        [ list.append(content.text) for content in information ]
        #print(list)
        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    browser.close()

    return redirect('cms:category_list')


def category_upload(request):
    """
    """

    print("category upload function")

    file = open("fixtures/categorias.txt","r")
    for line in file:
        print(len(line))
        if len(line) > 57:
            print(line)
            previous = ''
            attribute = ''
            list = []
            for letter in line:
                if letter != "[" and letter != "]":
                    if letter == ',':
                        if previous == "'":
                            print(attribute)
                            list.append(attribute.strip())
                            attribute = ''
                        else:
                            attribute += letter
                    elif letter == "'":
                        pass
                    else:
                        attribute += letter
                previous = letter
            print(list)

            cms_models.Categoria.objects.get_or_create(
                estado='Activo',
                titulo=list[1],
                en_titulo=list[2],
                subtitulo=list[3],
                en_subtitulo=list[4],
                prioridad=list[7],
                color=list[6]
            )

    file.close()


    file = open("fixtures/subcategorias.txt","r")

    for line in file:
        if len(line) > 47:
            previous = ''
            attribute = ''
            list = []
            for letter in line:
                if letter != "[" and letter != "]":
                    if letter == ',':
                        if previous == "'":
                            list.append(attribute.strip())
                            attribute = ''
                        else:
                            attribute += letter
                    elif letter == "'":
                        pass
                    else:
                        attribute += letter
                previous = letter

            try:
                parent_category = cms_models.Categoria.objects.get(titulo=list[3])
                print(parent_category)

            except cms_models.Categoria.DoesNotExist:
                parent_category = None
                print("not exist")

            except cms_models.Categoria.MultipleObjectsReturned:
                tmp = cms_models.Categoria.objects.filter(titulo=list[3].strip())
                parent_category = tmp[0]
                print("more than one")

            try:
                subcategory = cms_models.Categoria.objects.get_or_create(
                    estado='Activo',
                    titulo=list[1],
                    en_titulo=list[2],
                    prioridad=list[5],
                    categoria_padre=parent_category
                )
            except cms_models.Categoria.DoesNotExist:
                print("error")

    file.close()

    return redirect('cms:category_list')


def getCategoryUrls():

    urls = {
        'list': 'cms:category_list',
        'create': 'cms:category_create',
        'update': 'cms:category_update',
        'view': 'cms:category_view',
        'delete': 'cms:category_delete',
        'filter': 'cms:category_filter',
        'scrap': 'cms:category_scrap',
        'upload': 'cms:category_upload',
    }

    return urls


#Place Views
@login_required()
def place_list(request, filter_dict=None):
    """
    """

    print("place list function")

    title = 'Lugares'

    if filter_dict is None: #comprobamos si no pasamos algo de place_filter
        print("filter dict is none")
        filter_dict = request.GET.copy() #probamos a coger el diccionario de filtros del metodo get
    else:
        print("filter dict is not none")

    if filter_dict is not None:
        print("filter dict is not none")

        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        print(filter_dict)
        elements = place_filter_2(filter_dict)
    else:
        print("filter dict is none")
        elements = cms_models.Lugar.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = []
    exclude = ['en_titulo', 'subtitulo', 'en_subtitulo', 'en_informacion', 'informacion', 'servicios', 'en_servicios', 'latitud', 'longitud', 'telefono1', 'telefono2', 'url', 'reserva', 'compra', 'vista360', 'email', 'facebook', 'twitter', 'instagram']
    [fields.append(field) for field in cms_models.Lugar._meta.fields if field.name not in exclude]

    urls = getPlaceUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    if page is None:
        page = 1

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)

    print(filter_dict)

    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def place_create(request):
    """
    """

    print("place create function")

    title = 'Nuevo Luagr'
    urls = getPlaceUrls()

    if request.method == 'POST':
        form = cms_forms.PlaceForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('cms:place_list')
    else:
        form = cms_forms.PlaceForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def place_update(request, id=None):
    """
    """

    print("place update function")

    title = 'Editar Lugar'
    element = get_object_or_404(cms_models.Lugar, id=id)
    urls = getPlaceUrls()

    if request.method == 'POST':
        form = cms_forms.PlaceForm(request.POST, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:place_list')
    else:
        form = cms_forms.PlaceForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def place_view(request, id=None):
    """
    """

    print("place view function")

    title = 'Ver Lugar'
    element = get_object_or_404(cms_models.Lugar, id=id)

    content_type = get_object_or_404(ContentType, model='lugar')
    images = cms_models.Imagen.objects.filter(content_type_id=content_type.id, object_id=id)
    videos = cms_models.Video.objects.filter(content_type_id=content_type.id, object_id=id)

    list = {}
    for field in element._meta.fields:
        list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
        'images': images,
        'videos': videos
    })


@login_required()
def place_delete(request, id=None):
    """
    """

    print("place delete function")

    title = 'Borrar Lugar'
    element = get_object_or_404(cms_models.Lugar, id=id)
    urls = getPlaceUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:place_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def place_filter_2(filter_dict):
    """
    """

    print("place filter 2 function")

    elements = cms_models.Lugar.objects.all().order_by('-id')

    if filter_dict.get('status') is not None:
        elements = elements.filter(
        Q(estado=filter_dict['status']))

    if filter_dict.get('text') is not None:
        elements = elements.filter(
        Q(titulo__icontains=filter_dict["text"]) |
        Q(en_titulo__icontains=filter_dict["text"]) |
        Q(subtitulo__icontains=filter_dict["text"]) |
        Q(en_subtitulo__icontains=filter_dict["text"]) |
        Q(informacion__icontains=filter_dict["text"]) |
        Q(en_informacion__icontains=filter_dict["text"]) |
        Q(servicios__icontains=filter_dict["text"]) |
        Q(en_servicios__icontains=filter_dict["text"]))

    if filter_dict.get('start_date') is not None:
        elements = elements.filter(
        Q(created_date__gte=filter_dict['start_date']))

    if filter_dict.get('end_date') is not None:
        elements = elements.filter(
        Q(created_date__lte=filter_dict['end_date']))

    if filter_dict.get('start_priority') is not None:
        elements = elements.filter(
        Q(prioridad__gte=filter_dict['start_priority']))

    if filter_dict.get('end_priority') is not None:
        elements = elements.filter(
        Q(prioridad__lte=filter_dict['end_priority']))

    if filter_dict.get('categoria') is not None:
        elements = elements.filter(categoria_id=filter_dict['categoria'].id)

    if filter_dict.get('start_rank') is not None:
        elements = elements.filter(
        Q(puntuacion__gte=filter_dict['start_rank']))

    if filter_dict.get('end_rank') is not None:
        elements = elements.filter(
        Q(puntuacion__lte=filter_dict['end_rank']))

    if filter_dict.get('destacado') is True:
        elements = elements.filter(
        Q(destacado=1))

    return elements


@login_required()
def place_filter(request):
    """
    """

    print("place filter function")

    title = 'Filtrar Lugares'
    ##elements = cms_models.Lugar.objects.all()
    urls = getPlaceUrls()

    if request.method == 'POST':
        print("POST")
        filter_dict = {}
        form = cms_forms.PlaceFilterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data['status'] is not None:
                filter_dict['status'] = data['status']

            if data['text'] is not None:
                filter_dict['text'] = data['text']

            if data['start_date'] is not None:
                filter_dict['start_date'] = data['start_date']

            if data['end_date'] is not None:
                filter_dict['end_date'] = data['end_date']

            if data['start_priority'] is not None:
                filter_dict['start_priority'] = data['start_priority']

            if data['end_priority'] is not None:
                filter_dict['end_priority'] = data['end_priority']

            if data['categoria'] is not None:
                filter_dict['categoria'] = data['categoria']

            if data['start_rank'] is not None:
                filter_dict['start_rank'] = data['start_rank']

            if data['end_rank'] is not None:
                filter_dict['end_rank'] = data['end_rank']

            if data['destacado'] is True:
                filter_dict['destacado'] = data['destacado']

            return place_list(request, filter_dict)

    else:
        print("GET")
        form = cms_forms.PlaceFilterForm()

    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
    })


@login_required()
def place_scrap(request):
    """
    scrap with selenium all publications
    """

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path='/Users/albertosanmartinmartinez/Downloads/chromedriver', chrome_options=option)
    browser.get('http://salamantica.com/cms/login')

    timeout = 5

    WebDriverWait(browser, timeout)

    browser.find_element_by_id("UserUsername").send_keys("rubenmartin@salamancamovil.com")
    browser.find_element_by_id("UserPassword").send_keys("D*JT3T6QDRkYc))TflBn)CH&")
    browser.find_element_by_css_selector('button[type="submit"]').click()

    WebDriverWait(browser, timeout)

    file = open("fixtures/lugares.txt","w")
    category_web = 'http://salamantica.com/cms/places/edit/'

    for i in range(1, 559):
        list = []

        browser.get(category_web + str(i))
        WebDriverWait(browser, timeout)
        select = Select(browser.find_element_by_id('PlaceCategoryId'))
        list.append(select.first_selected_option.text)
        select = Select(browser.find_element_by_id('PlaceSubcategoryId'))
        list.append(select.first_selected_option.text)
        select = browser.find_element_by_id('PlaceName')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceNameEn')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceInfo')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceInfoEn')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlacePriority')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceRank')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceCost')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceCostEn')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceLocationPositionLatitude')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceLocationPositionLongitude')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceServices')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceServicesEn')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlacePhone')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceUrl')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceUrlAction')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceUrlBuy')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PlaceUrlTour')
        list.append(select.get_attribute('value'))

        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    browser.close()
    return redirect('cms:place_list')


def place_upload(request):
    """
    """
    from decimal import Decimal

    file = open("fixtures/lugares.txt","r")

    for line in file:
        #print(line)
        #print(len(line))
        if len(line) > 109:
            previous = ''
            attribute = ''
            list = []
            for letter in line:
                if letter != '[':
                    if letter == ',' or letter == "]":
                        if previous == "'" or previous == '"':
                            #print(attribute)
                            #print(type(attribute))
                            list.append(attribute.strip())
                            attribute = ''
                        else:
                            attribute += letter
                    else:
                        attribute += letter
                    previous = letter

            aux=[]
            [aux.append(item.strip("'")) for item in list]
            #print(aux)
            #print(len(aux))

            try:
                category = cms_models.Categoria.objects.get(
                    titulo=aux[1]
                )
                #print(category)

            except cms_models.Categoria.DoesNotExist:
                category = None
                print(aux[1])
                print("not exit")

            except cms_models.Categoria.MultipleObjectsReturned:
                category = cms_models.Categoria.objects.filter(titulo=aux[1].strip())[0]
                print(category)
                #category = tmp[0]
                print("more than one")

            try:
                place = cms_models.Lugar.objects.get_or_create(
                    estado='Activo',
                    titulo=aux[2],
                    en_titulo=aux[3],
                    informacion=aux[4],
                    en_informacion=aux[5],
                    prioridad=aux[6],
                    categoria=category,
                    puntuacion=aux[7],
                    servicios=aux[12],
                    en_servicios=aux[13],
                    latitud=aux[10],
                    longitud=aux[11],
                    telefono1=aux[14],
                    url=aux[15],
                    reserva=aux[16],
                    compra=aux[17],
                    vista360=aux[18])

            except cms_models.Lugar.DoesNotExist:
                print("error")


    file.close()

    return redirect('cms:category_list')


def getPlaceUrls():

    urls = {
        'list': 'cms:place_list',
        'create': 'cms:place_create',
        'update': 'cms:place_update',
        'view': 'cms:place_view',
        'delete': 'cms:place_delete',
        'filter': 'cms:place_filter',
        'scrap': 'cms:place_scrap',
        'upload': 'cms:place_upload',
    }

    return urls


# Promotion Views
@login_required()
def promo_list(request, filter_dict=None):
    """
    """

    print("promo list function")

    title = 'Promociones'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = promo_filter_2(filter_dict)

    else:
        elements = cms_models.Promo.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = []
    exclude = ['en_titulo', 'subtitulo', 'en_subtitulo', 'en_informacion', 'informacion']
    [fields.append(field) for field in cms_models.Promo._meta.fields if field.name not in exclude]

    urls = getPromoUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    if page is None:
        page = 1

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def promo_create(request):
    """
    """

    print("promo create function")

    title = 'Nueva Promoción'
    urls = getPromoUrls()

    if request.method == 'POST':
        form = cms_forms.PromoForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('cms:promo_list')
    else:
        form = cms_forms.PromoForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def promo_update(request, id=None):
    """
    """

    print("promo update function")

    title = 'Editar Promo'
    element = get_object_or_404(cms_models.Promo, id=id)
    urls = getPromoUrls()

    if request.method == 'POST':
        form = cms_forms.PromoForm(request.POST, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:promo_list')
    else:
        form = cms_forms.PromoForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def promo_view(request, id=None):
    """
    """

    print("promo view function")

    title = 'Ver Promo'
    element = get_object_or_404(cms_models.Promo, id=id)

    content_type = get_object_or_404(ContentType, model='promo')
    images = cms_models.Imagen.objects.filter(content_type_id=content_type.id, object_id=id)
    videos = cms_models.Video.objects.filter(content_type_id=content_type.id, object_id=id)

    list = {}
    for field in element._meta.fields:
        list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
        'images': images,
        'videos': videos
    })


@login_required()
def promo_delete(request, id=None):
    """
    """

    print("promo delete function")

    title = 'Borrar Promo'
    element = get_object_or_404(cms_models.Promo, id=id)
    urls = getPromoUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:promo_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def promo_filter_2(filter_dict):
    """
    """

    print("promo filter 2 function")

    elements = cms_models.Promo.objects.all()

    if filter_dict.get('status') is not None:
        elements = elements.filter(
        Q(estado=filter_dict['status']))

    if filter_dict.get('text') is not None:
        elements = elements.filter(
        Q(titulo__icontains=filter_dict["text"]) |
        Q(en_titulo__icontains=filter_dict["text"]) |
        Q(subtitulo__icontains=filter_dict["text"]) |
        Q(en_subtitulo__icontains=filter_dict["text"]) |
        Q(informacion__icontains=filter_dict["text"]) |
        Q(en_informacion__icontains=filter_dict["text"]))

    if filter_dict.get('start_date') is not None:
        elements = elements.filter(
        Q(created_date__gte=filter_dict['start_date']))

    if filter_dict.get('end_date') is not None:
        elements = elements.filter(
        Q(created_date__lte=filter_dict['end_date']))

    if filter_dict.get('start_priority') is not None:
        elements = elements.filter(
        Q(prioridad__gte=filter_dict['start_priority']))

    if filter_dict.get('end_priority') is not None:
        elements = elements.filter(
        Q(prioridad__lte=filter_dict['end_priority']))

    if filter_dict.get('place') is not None:
        place = get_object_or_404(cms_models.Lugar, titulo=filter_dict['place'])
        elements = elements.filter(lugar_id=place.id)

    return elements


@login_required()
def promo_filter(request):
    """
    """

    print("promo filter function")

    title = 'Filtrar Promos'
    urls = getPromoUrls()

    if request.method == 'POST':
        filter_dict = {}
        form = cms_forms.PromoFilterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data['status'] is not None:
                filter_dict['status'] = data['status']

            if data['text'] is not None:
                filter_dict['text'] = data["text"]

            if data['start_date'] is not None:
                filter_dict['start_date'] = data['start_date']

            if data['end_date'] is not None:
                filter_dict['end_date'] = data['end_date']

            if data['start_priority'] is not None:
                filter_dict['start_priority'] = data['start_priority']

            if data['end_priority'] is not None:
                filter_dict['end_priority'] = data['end_priority']

            if data['place'] is not None:
                filter_dict['place'] = data['place'].titulo

            return promo_list(request, filter_dict)
    else:
        form = cms_forms.PromoFilterForm()

    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
    })


@login_required()
def promo_scrap(request):
    """
    scrap with selenium all promotions
    """

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path='/Users/albertosanmartinmartinez/Downloads/chromedriver', chrome_options=option)
    browser.get('http://salamantica.com/cms/login')

    timeout = 5

    WebDriverWait(browser, timeout)

    browser.find_element_by_id("UserUsername").send_keys("rubenmartin@salamancamovil.com")
    browser.find_element_by_id("UserPassword").send_keys("D*JT3T6QDRkYc))TflBn)CH&")
    browser.find_element_by_css_selector('button[type="submit"]').click()

    WebDriverWait(browser, timeout)

    file = open("fixtures/promociones.txt","w")
    category_web = 'http://salamantica.com/cms/promos/view/'

    for i in range(1, 53):
        list = []

        browser.get(category_web + str(i))
        WebDriverWait(browser, timeout)
        information = browser.find_elements_by_class_name('controls')
        [ list.append(content.text) for content in information ]
        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    browser.close()

    return redirect('cms:promo_list')


def promo_upload(request):
    """
    """

    file = open("fixtures/promociones.txt", "r")

    for line in file:
        #print(line)
        #print(len(line))
        if len(line) > 52:
            previous = ''
            attribute = ''
            list = []
            for letter in line:
                if letter != '[':
                    if letter == ',' or letter == "]":
                        if previous == "'" or previous == '"':
                            print(attribute)
                            #print(type(attribute))
                            list.append(attribute.strip())
                            attribute = ''
                        else:
                            attribute += letter
                    else:
                        attribute += letter
                    previous = letter

            aux=[]
            [aux.append(item.strip("'")) for item in list]
            print(aux)
            #print(len(aux))

            try:
                place = cms_models.Lugar.objects.get(titulo=aux[1])
                print(place)
            except cms_models.Lugar.DoesNotExist:
                place = None
            except cms_models.Lugar.MultipleObjectsReturned:
                place = None

            try:
                promo = cms_models.Promo.objects.get_or_create(
                    estado='Activo',
                    titulo=aux[2],
                    en_titulo=aux[4],
                    informacion=aux[5],
                    en_informacion=aux[3],
                    prioridad=aux[6],
                    lugar=place)
            except cms_models.Promo.DoesNotExist:
                print("error")

    file.close()

    return redirect('cms:promo_list')


def getPromoUrls():

    urls = {
        'list': 'cms:promo_list',
        'create': 'cms:promo_create',
        'update': 'cms:promo_update',
        'view': 'cms:promo_view',
        'delete': 'cms:promo_delete',
        'filter': 'cms:promo_filter',
        'scrap': 'cms:promo_scrap',
        'upload': 'cms:promo_upload',
    }

    return urls


# Price Views
@login_required()
def price_list(request, filter_dict=None):
    """
    """

    print("price list function")

    title = 'Precios'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = price_filter_2(filter_dict)

    else:
        elements = cms_models.Precio.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = []
    exclude = ['en_titulo', 'en_subtitulo', 'en_informacion', 'subtitulo', 'informacion']
    [fields.append(field) for field in cms_models.Precio._meta.fields if field.name not in exclude]

    urls = getPriceUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    if page is None:
        page = 1

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def price_create(request):
    """
    """

    print("price create function")

    title = 'Nuevo Precio'
    urls = getPriceUrls()

    if request.method == 'POST':
        form = cms_forms.PrecioForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('cms:price_list')
    else:
        form = cms_forms.PrecioForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def price_update(request, id=None):
    """
    """

    print("price update function")

    title = 'Editar Precio'
    element = get_object_or_404(cms_models.Precio, id=id)
    urls = getPriceUrls()

    if request.method == 'POST':
        form = cms_forms.PrecioForm(request.POST, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:price_list')
    else:
        form = cms_forms.PrecioForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def price_view(request, id=None):
    """
    """

    print("price view function")

    title = 'Ver Precio'
    element = get_object_or_404(cms_models.Precio, id=id)

    list = {}
    for field in element._meta.fields:
        list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
    })


@login_required()
def price_delete(request, id=None):
    """
    """

    print("price delete function")

    title = 'Borrar Precio'
    element = get_object_or_404(cms_models.Precio, id=id)
    urls = getPriceUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:price_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def price_filter_2(filter_dict):
    """
    """

    print("price filter function")

    elements = cms_models.Precio.objects.all()

    if filter_dict.get('status') is not None:
        elements = elements.filter(
        Q(estado=filter_dict['status']))

    if filter_dict.get('text') is not None:
        elements = elements.filter(
        Q(titulo__icontains=filter_dict["text"]) |
        Q(en_titulo__icontains=filter_dict["text"]) |
        Q(subtitulo__icontains=filter_dict["text"]) |
        Q(en_subtitulo__icontains=filter_dict["text"]) |
        Q(informacion__icontains=filter_dict["text"]) |
        Q(en_informacion__icontains=filter_dict["text"]))

    if filter_dict.get('start_date') is not None:
        elements = elements.filter(
        Q(created_date__gte=filter_dict['start_date']))

    if filter_dict.get('end_date') is not None:
        elements = elements.filter(
        Q(created_date__lte=filter_dict['end_date']))

    if filter_dict.get('start_priority') is not None:
        elements = elements.filter(
        Q(prioridad__gte=filter_dict['start_priority']))

    if filter_dict.get('end_priority') is not None:
        elements = elements.filter(
        Q(prioridad__lte=filter_dict['end_priority']))

    if filter_dict.get('place') is not None:
        elements = elements.filter(lugar_id=filter_dict['place'].id)

    if filter_dict.get('start_price') is not None:
        elements = elements.filter(
        Q(cantidad__gte=filter_dict['start_price']))

    if filter_dict.get('end_price') is not None:
        elements = elements.filter(
        Q(cantidad__lte=filter_dict['end_price']))

    return elements


@login_required()
def price_filter(request):
    """
    """

    print("price filter function")

    title = 'Filtrar Precios'
    urls = getPriceUrls()

    if request.method == 'POST':
        filter_dict = {}
        form = cms_forms.PrecioFilterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data['status'] is not None:
                filter_dict['status'] = data['status']

            if data['text'] is not None:
                filter_dict['text'] = data["text"]

            if data['start_date'] is not None:
                filter_dict['start_date'] = data['start_date']

            if data['end_date'] is not None:
                filter_dict['end_date'] = data['end_date']

            if data['start_priority'] is not None:
                filter_dict['start_priority'] = data['start_priority']

            if data['end_priority'] is not None:
                filter_dict['end_priority'] = data['end_priority']

            if data['place'] is not None:
                filter_dict['place'] = data['place']

            if data['start_price'] is not None:
                filter_dict['start_price'] = data['start_price']

            if data['end_price'] is not None:
                filter_dict['end_price'] = data['end_price']

            return price_list(request, filter_dict)
    else:
        form = cms_forms.PrecioFilterForm()


    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
    })


@login_required()
def price_scrap(request):
    """
    scrap with selenium all prices
    """

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path='/Users/albertosanmartinmartinez/Downloads/chromedriver', chrome_options=option)
    browser.get('http://salamantica.com/cms/login')

    timeout = 5

    WebDriverWait(browser, timeout)

    browser.find_element_by_id("UserUsername").send_keys("rubenmartin@salamancamovil.com")
    browser.find_element_by_id("UserPassword").send_keys("D*JT3T6QDRkYc))TflBn)CH&")
    browser.find_element_by_css_selector('button[type="submit"]').click()

    WebDriverWait(browser, timeout)

    file = open("fixtures/precios.txt","w")
    category_web = 'http://salamantica.com/cms/prices/view/'

    for i in range(1, 314):
        list = []

        browser.get(category_web + str(i))
        WebDriverWait(browser, timeout)
        information = browser.find_elements_by_class_name('controls')
        [ list.append(content.text) for content in information ]
        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    browser.close()

    return redirect('cms:price_list')


def price_upload(request):
    """
    """

    file = open("fixtures/precios.txt", "r")

    for line in file:
        print(line)
        #print(len(line))
        if len(line) > 62:
            previous = ''
            attribute = ''
            list = []
            for letter in line:
                if letter != '[':
                    if letter == ',' or letter == "]":
                        if previous == "'" or previous == '"':
                            print(attribute)
                            #print(type(attribute))
                            list.append(attribute.strip())
                            attribute = ''
                        else:
                            attribute += letter
                    else:
                        attribute += letter
                    previous = letter

            aux=[]
            [aux.append(item.strip("'")) for item in list]
            #print(aux)
            #print(len(aux))

            try:
                place = cms_models.Lugar.objects.get(titulo=aux[1].strip())
                print(place)

            except cms_models.Lugar.DoesNotExist:
                place = None
                print("not exist")

            except cms_models.Lugar.MultipleObjectsReturned:
                tmp = cms_models.Lugar.objects.filter(titulo=aux[1].strip())
                place = tmp[0]
                print("more than one")

            try:
                promo = cms_models.Precio.objects.get_or_create(
                    estado='Activo',
                    titulo=aux[2],
                    en_titulo=aux[3],
                    #informacion=aux[5],
                    #en_informacion=aux[3],
                    #cantidad=Decimal(aux[4]),
                    prioridad=aux[8],
                    lugar=place)
            except cms_models.Precio.DoesNotExist:
                print("error")

    file.close()

    return redirect('cms:price_list')


def getPriceUrls():

    urls = {
        'list': 'cms:price_list',
        'create': 'cms:price_create',
        'update': 'cms:price_update',
        'view': 'cms:price_view',
        'delete': 'cms:price_delete',
        'filter': 'cms:price_filter',
        'scrap': 'cms:price_scrap',
        'upload': 'cms:price_upload',
    }

    return urls


# Schedule Views
@login_required()
def schedule_list(request, filter_dict=None):

    """
    """

    print("schedule list function")

    title = 'Horarios'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = schedule_filter_2(filter_dict)

    else:
        elements = cms_models.Horario.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = []
    exclude = ['en_titulo', 'subtitulo', 'informacion', 'en_subtitulo', 'en_informacion']
    [fields.append(field) for field in cms_models.Horario._meta.fields if field.name not in exclude]

    urls = getScheduleUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    if page is None:
        page = 1

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def schedule_create(request):
    """
    generic formset with model and form
    add and delete form formset in templates
    """

    from django import forms

    print("schedule create function")

    title = 'Nuevo Horario'
    urls = getScheduleUrls()

    if request.method == 'POST':
        form = cms_forms.HorarioForm(request.POST)
        formset = cms_forms.PeriodoHorarioFormset(request.POST)

        if formset.is_valid() and form.is_valid():
            schedule = form.save()

            for formset_form in formset:
                if formset_form.is_valid():
                    print(formset_form.cleaned_data)
                    schedule_period = formset_form.save(commit=False)
                    schedule_period.horario = schedule
                    schedule_period.save()

                else:
                    print("formset_form invalid")
                    print(formset_form.errors)

            return redirect('cms:schedule_list')

        else:
            print(formset.errors)
            print(form.errors)

            return redirect('cms:schedule_list')

    else:
        form = cms_forms.HorarioForm()
        formset = cms_forms.PeriodoHorarioFormset(queryset=cms_models.Horario.objects.none())

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'formset': formset,
        'urls': urls,
    })


@login_required()
def schedule_update(request, id=None):
    """
    """

    print("schedule update function")

    title = 'Editar Horario'
    element = get_object_or_404(cms_models.Horario, id=id)
    urls = getScheduleUrls()
    query = cms_models.PeriodoHorario.objects.filter(horario=element)
    #print(query)

    if request.method == 'POST':
        print("POST")
        form = cms_forms.HorarioForm(request.POST, instance=element)
        formset = cms_forms.PeriodoHorarioFormset(request.POST, queryset=query)

        if formset.is_valid() and form.is_valid():
            schedule = form.save()
            print(schedule)

            for formset_form in formset:
                if formset_form.is_valid():
                    print("formulario valido")
                    #print(formset_form)
                    schedule_period = formset_form.save(commit=False)
                    schedule_period.horario = schedule
                    schedule_period.save()
                    #formset_form.save()

                else:
                    print(formset_form.errors)

            return redirect('cms:schedule_list')

        else:
            print(formset.errors)
            print(form.errors)

            return redirect('cms:schedule_list')

    else:
        print("GET")
        form = cms_forms.HorarioForm(instance=element)
        formset = cms_forms.PeriodoHorarioFormset(queryset=query) #, initial={'extra':0})

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'formset': formset,
        'urls': urls,
    })


@login_required()
def schedule_view(request, id=None):
    """
    """

    print("schedule view function")

    title = 'Ver Horario'
    element = get_object_or_404(cms_models.Horario, id=id)

    fields = []
    model_fields = cms_models.Horario._meta.get_fields()
    exclude_fields = []
    [fields.append(field) for field in model_fields if field.name not in exclude_fields]

    list = {}
    for field in fields:
        attribute_class_name = field.__class__.__name__
        if attribute_class_name == 'ManyToManyField':
            pass
        elif attribute_class_name == 'ManyToOneRel':
            pass
            #schedule_periods = cms_models.PeriodoHorario.objects.filter(horario_id=element.id)

        #elif attribute_class_name == 'ForeignKey':
        #    print(field)

        else:
            list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
    })


@login_required()
def schedule_delete(request, id=None):
    """
    """

    print("schedule delete function")

    title = 'Borrar Horario'
    element = get_object_or_404(cms_models.Horario, id=id)
    urls = getScheduleUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:schedule_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def schedule_filter_2(filter_dict):
    """
    """

    print("schedule filter function")

    elements = cms_models.Horario.objects.all()

    if filter_dict.get('text') is not None:
        elements = elements.filter(
        Q(titulo__icontains=filter_dict["text"]) |
        Q(en_titulo__icontains=filter_dict["text"]) |
        Q(subtitulo__icontains=filter_dict["text"]) |
        Q(en_subtitulo__icontains=filter_dict["text"]) |
        Q(informacion__icontains=filter_dict["text"]) |
        Q(en_informacion__icontains=filter_dict["text"]))

    if filter_dict.get('start_date') is not None:
        elements = elements.filter(
        Q(created_date__gte=filter_dict['start_date']))

    if filter_dict.get('end_date') is not None:
        elements = elements.filter(
        Q(created_date__lte=filter_dict['end_date']))

    if filter_dict.get('start_priority') is not None:
        elements = elements.filter(
        Q(prioridad__gte=filter_dict['start_priority']))

    if filter_dict.get('end_priority') is not None:
        elements = elements.filter(
        Q(prioridad__lte=filter_dict['end_priority']))

    if filter_dict.get('place') is not None:
        elements = elements.filter(lugar_id=filter_dict['place'].id)

    return elements


@login_required()
def schedule_filter(request):
    """
    """

    print("schedule filter function")

    title = 'Filtrar Horarios'
    urls = getScheduleUrls()

    if request.method == 'POST':
        filter_dict = {}
        form = cms_forms.HorarioFilterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data['text'] is not None:
                filter_dict['status'] = data["text"]

            if data['start_date'] is not None:
                filter_dict['status'] = data['start_date']

            if data['end_date'] is not None:
                filter_dict['status'] = data['end_date']

            if data['start_priority'] is not None:
                filter_dict['status'] = data['start_priority']

            if data['end_priority'] is not None:
                filter_dict['status'] = data['end_priority']

            if data['place'] is not None:
                filter_dict['status'] = data['place'].titulo

            return schedule_list(request, filter_dict)
    else:
        form = cms_forms.HorarioFilterForm()

    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
    })


@login_required()
def schedule_scrap(request):
    """
    scrap with selenium all schedules
    """

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path='/Users/albertosanmartinmartinez/Downloads/chromedriver', chrome_options=option)
    browser.get('http://salamantica.com/cms/login')

    timeout = 5

    WebDriverWait(browser, timeout)

    browser.find_element_by_id("UserUsername").send_keys("rubenmartin@salamancamovil.com")
    browser.find_element_by_id("UserPassword").send_keys("D*JT3T6QDRkYc))TflBn)CH&")
    browser.find_element_by_css_selector('button[type="submit"]').click()

    WebDriverWait(browser, timeout)

    file = open("fixtures/horarios.txt","w")
    category_web = 'http://salamantica.com/cms/schedules/view/'

    for i in range(1, 354):
        list = []

        browser.get(category_web + str(i))
        WebDriverWait(browser, timeout)
        information = browser.find_elements_by_class_name('controls')
        [ list.append(content.text) for content in information ]
        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    browser.close()

    return redirect('cms:schedule_list')


def schedule_upload(request):
    """
    """

    import datetime

    file = open("fixtures/horarios.txt", "r")

    i = 1
    for line in file:
        #print(line)
        #print(len(line))
        #print(i)
        i += 1
        if len(line) > 62:
            previous = ''
            attribute = ''
            list = []
            for letter in line:
                if letter != '[':
                    if letter == ',' or letter == "]":
                        if previous == "'" or previous == '"':
                            #print(attribute)
                            #print(type(attribute))
                            list.append(attribute.strip())
                            attribute = ''
                        else:
                            attribute += letter
                    else:
                        attribute += letter
                    previous = letter

            aux=[]
            [aux.append(item.strip("'")) for item in list]
            #print(aux)
            #print(len(aux))

            try:
                place = cms_models.Lugar.objects.get(titulo=aux[1].strip())
                print(place)

            except cms_models.Lugar.DoesNotExist:
                place = None
                print("not exist")

            except cms_models.Lugar.MultipleObjectsReturned:
                tmp = cms_models.Lugar.objects.filter(titulo=aux[1].strip())
                place = tmp[0]
                print("more than one")

            try:
                schedule = cms_models.Horario.objects.get_or_create(
                    estado='Activo',
                    titulo=aux[2],
                    en_titulo=aux[3],
                    subtitulo=aux[4],
                    en_subtitulo=aux[5],
                    informacion=aux[6],
                    en_informacion=aux[7],
                    prioridad=aux[8],
                    lugar=place
                )

                schdule_period = cms_models.PeriodoHorario.objects.get_or_create(
                    horario=schedule[0],
                    inicio=datetime.datetime.now().time(),
                    fin=datetime.datetime.now().time()
                )

            except cms_models.Horario.DoesNotExist:
                print("error")

    file.close()

    return redirect('cms:schedule_list')


def getScheduleUrls():

    urls = {
        'list': 'cms:schedule_list',
        'create': 'cms:schedule_create',
        'update': 'cms:schedule_update',
        'view': 'cms:schedule_view',
        'delete': 'cms:schedule_delete',
        'filter': 'cms:schedule_filter',
        'scrap': 'cms:schedule_scrap',
        'upload': 'cms:schedule_upload',
    }

    return urls


# Publication Views
@login_required()
def publication_list(request, filter_dict=None):

    """
    """

    print("publication list function")

    title = 'Publicaciones'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = publication_filter_2(filter_dict)

    else:
        elements = cms_models.Publicacion.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = []
    exclude = ['en_titulo', 'subtitulo', 'en_subtitulo', 'en_informacion', 'informacion']
    [fields.append(field) for field in cms_models.Publicacion._meta.fields if field.name not in exclude]

    urls = getPublicationUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    if page is None:
        page = 1

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def publication_create(request):
    """
    """

    print("publication create function")

    title = 'Nueva Publicación'
    urls = getPublicationUrls()

    if request.method == 'POST':
        form = cms_forms.PublicacionForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('cms:publication_list')
    else:
        form = cms_forms.PublicacionForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def publication_update(request, id=None):
    """
    """

    print("publication update function")

    title = 'Editar Publicación'
    element = get_object_or_404(cms_models.Publicacion, id=id)
    urls = getPublicationUrls()

    if request.method == 'POST':
        form = cms_forms.PublicacionForm(request.POST, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:publication_list')
    else:
        form = cms_forms.PublicacionForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def publication_view(request, id=None):
    """
    """

    print("publication view function")

    title = 'Ver Publicación'
    element = get_object_or_404(cms_models.Publicacion, id=id)

    content_type = get_object_or_404(ContentType, model='publicacion')
    images = cms_models.Imagen.objects.filter(content_type_id=content_type.id, object_id=id)
    videos = cms_models.Video.objects.filter(content_type_id=content_type.id, object_id=id)

    list = {}
    for field in element._meta.fields:
        list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
        'images': images,
        'videos': videos
    })


@login_required()
def publication_delete(request, id=None):
    """
    """

    print("publication delete function")

    title = 'Borrar Publicación'
    element = get_object_or_404(cms_models.Publicacion, id=id)
    urls = getPublicationUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:publication_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def publication_filter_2(filter_dict):
    """
    """

    print("publication filter 2 function")

    elements = cms_models.Publicacion.objects.all()

    #print(filter_dict)

    if filter_dict.get('status') is not None:
        elements = elements.filter(
        Q(estado=filter_dict['status']))

    if filter_dict.get('text') is not None:
        elements = elements.filter(
        Q(titulo__icontains=filter_dict["text"]) |
        Q(en_titulo__icontains=filter_dict["text"]) |
        Q(subtitulo__icontains=filter_dict["text"]) |
        Q(en_subtitulo__icontains=filter_dict["text"]) |
        Q(informacion__icontains=filter_dict["text"]) |
        Q(en_informacion__icontains=filter_dict["text"]))

    if filter_dict.get('start_date') is not None:
        elements = elements.filter(
        Q(created_date__gte=filter_dict['start_date']))

    if filter_dict.get('end_date') is not None:
        elements = elements.filter(
        Q(created_date__lte=filter_dict['end_date']))

    if filter_dict.get('start_priority') is not None:
        elements = elements.filter(
        Q(prioridad__gte=filter_dict['start_priority']))

    if filter_dict.get('end_priority') is not None:
        elements = elements.filter(
        Q(prioridad__lte=filter_dict['end_priority']))

    if filter_dict.get('categoria') is not None:
        categoria = get_object_or_404(cms_models.Categoria, titulo=filter_dict['categoria'])
        elements = elements.filter(categoria_id=categoria.id)

    if filter_dict.get('type') is not None:
        elements = elements.filter(
        Q(tipo=filter_dict['type']))

    return elements


@login_required()
def publication_filter(request):
    """
    """

    print("publication filter function")

    title = 'Filtrar Publicaciones'
    urls = getPublicationUrls()

    if request.method == 'POST':
        filter_dict = {}
        form = cms_forms.PublicacionFilterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data['status'] is not None:
                filter_dict['status'] = data['status']

            if data['text'] is not None:
                filter_dict['text'] = data["text"]

            if data['start_date'] is not None:
                filter_dict['start_date'] = data['start_date']

            if data['end_date'] is not None:
                filter_dict['end_date'] = data['end_date']

            if data['start_priority'] is not None:
                filter_dict['start_priority'] = data['start_priority']

            if data['end_priority'] is not None:
                filter_dict['end_priority'] = data['end_priority']

            if data['categoria'] is not None:
                filter_dict['categoria'] = data['categoria'].titulo

            if data['type'] is not None:
                filter_dict['type'] = data['type']

            return publication_list(request, filter_dict)
    else:
        form = cms_forms.PublicacionFilterForm()


    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
    })


@login_required()
def publication_scrap(request):
    """
    scrap with selenium all publications
    """

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path='/Users/albertosanmartinmartinez/Downloads/chromedriver', chrome_options=option)
    browser.get('http://salamantica.com/cms/login')

    timeout = 5

    WebDriverWait(browser, timeout)

    browser.find_element_by_id("UserUsername").send_keys("rubenmartin@salamancamovil.com")
    browser.find_element_by_id("UserPassword").send_keys("D*JT3T6QDRkYc))TflBn)CH&")
    browser.find_element_by_css_selector('button[type="submit"]').click()

    WebDriverWait(browser, timeout)

    file = open("fixtures/publicaciones.txt","w")
    category_web = 'http://salamantica.com/cms/posts/edit/'

    for i in range(60, 111):
        list = []

        browser.get(category_web + str(i))
        WebDriverWait(browser, timeout)
        select = Select(browser.find_element_by_id('PostCategory'))
        list.append(select.first_selected_option.text)
        select = Select(browser.find_element_by_id('PostType'))
        list.append(select.first_selected_option.text)
        select = browser.find_element_by_id('PostTitle')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PostTitleEn')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PostContent')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PostContentEn')
        list.append(select.get_attribute('value'))
        select = browser.find_element_by_id('PostDate')
        list.append(select.get_attribute('value'))

        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    browser.close()

    return redirect('cms:publication_list')


def publication_upload(request):
    """
    """

    file = open("fixtures/publicaciones.txt","r")

    for line in file:
        #print(line)
        #print(len(line))
        if len(line) > 29:
            previous = ''
            attribute = ''
            list = []

            for letter in line:
                if letter != '[':
                    if letter == ',' or letter == "]":
                        if previous == "'" or previous == '"':
                            #print(attribute)
                            list.append(attribute.strip())
                            attribute = ''
                        else:
                            attribute += letter
                    else:
                        attribute += letter
                previous = letter

            aux=[]
            [aux.append(item.strip("'")) for item in list]
            #print(aux)
            #print(len(aux))

            try:
                category = cms_models.Categoria.objects.get(
                    titulo=aux[0])
                print(category)

            except cms_models.Categoria.DoesNotExist:
                category = None
                print("not exit")

            except cms_models.Categoria.MultipleObjectsReturned:
                tmp = cms_models.Categoria.objects.filter(titulo=aux[0].strip())
                category = tmp[0]
                print("more than one")

            try:
                publication = cms_models.Publicacion.objects.get_or_create(
                    estado='Activo',
                    tipo=aux[1].capitalize(),
                    titulo=aux[2],
                    en_titulo=aux[3],
                    informacion=aux[4],
                    en_informacion=aux[5],
                    categoria=category
                )
            except cms_models.Categoria.DoesNotExist:
                print("error")

    file.close()

    return redirect('cms:category_list')


def getPublicationUrls():

    urls = {
        'list': 'cms:publication_list',
        'create': 'cms:publication_create',
        'update': 'cms:publication_update',
        'view': 'cms:publication_view',
        'delete': 'cms:publication_delete',
        'filter': 'cms:publication_filter',
        'scrap': 'cms:publication_scrap',
        'upload': 'cms:publication_upload',
    }

    return urls



@login_required()
def user_list(request, filter_dict=None):
    """
    """

    print("user list function")

    title = 'Usuarios'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = user_filter_2(filter_dict)

    else:
        elements = cms_models.Categoria.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = []
    exclude = ['password', 'is_superuser', 'is_staff', 'last_login', 'date_joined', 'first_name', 'last_name']
    [fields.append(field) for field in User._meta.fields if field.name not in exclude]

    urls = getUserUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))

        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    if page is None:
        page = 1

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def user_create(request):
    """
    """

    print("user create function")

    title = 'Nuevo Usuario'
    urls = getUserUrls()

    if request.method == 'POST':
        form = cms_forms.SingupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create(
                is_active=False,
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )

            current_site = get_current_site(request)
            print(current_site)
            mail_subject = 'Restablecer contraseña - Valladolid CMS'
            from_email = settings.EMAIL_HOST_USER
            print(from_email)
            to_email = [user.email,]
            print(to_email)
            print(user.pk)
            message = render_to_string('email_password_reset.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(mail_subject, message, from_email, to_email, fail_silently=False,)

            return redirect('cms:user_list')
        else:
            print("invalid form")
    else:
        form = cms_forms.SingupForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def user_update(request, id=None):
    """
    """

    print("user update function")

    title = 'Editar Usuario'
    element = get_object_or_404(User, id=id)
    urls = getUserUrls()

    if request.method == 'POST':
        form = cms_forms.UserForm(request.POST, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:user_list')
    else:
        form = cms_forms.UserForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def user_view(request, id=None):
    """
    """

    print("user view function")

    title = 'Ver Usuario'
    element = get_object_or_404(User, id=id)

    fields = []
    exclude = ['password', 'is_superuser', 'is_staff']
    print(User._meta.fields)
    [fields.append(field) for field in User._meta.fields if field.name not in exclude]

    list = {}
    for field in fields:
        list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
    })


@login_required()
def user_delete(request, id=None):
    """
    """

    print("user delete function")

    title = 'Borrar Usuario'
    element = get_object_or_404(User, id=id)
    urls = getUserUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:user_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def user_filter_2(filter_dict):
    """
    """

    print("user filter 2 function")

    elements = User.objects.all()

    return elements


@login_required()
def user_filter(request):
    """
    """

    print("user filter function")

    title = 'Filtrar Usuarios'
    urls = getUserUrls()

    if request.method == 'POST':
        filter_dict = {}
        form = cms_forms.CategoryFilterForm(request.POST)
        if form.is_valid():
            return user_list(request, filter_dict)

    else:
        form = cms_forms.CategoryFilterForm()

    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
    })


def user_scrap(request):
    pass


def user_upload():
    pass


def getUserUrls():

    urls = {
        'list': 'cms:user_list',
        'create': 'cms:user_create',
        'update': 'cms:user_update',
        'view': 'cms:user_view',
        'delete': 'cms:user_delete',
        'filter': 'cms:user_filter',
        'scrap': 'cms:user_scrap',
        'upload': 'cms:user_upload',
    }

    return urls


# Image Views
@login_required()
def image_list(request, filter_dict=None):
    """
    """

    print("image list function")

    title = 'Imagenes'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = image_filter_2(filter_dict)

    else:
        elements = cms_models.Imagen.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = cms_models.Imagen._meta.fields
    urls = getImageUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def image_create(request):
    """
    """

    print("image create function")

    title = 'Nueva Imagen'
    urls = getImageUrls()

    if request.method == 'POST':
        """
        form = cms_forms.ImagenForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            return redirect('cms:image_list')
        """

        form = cms_forms.ImagenForm(request.POST)
        files = request.FILES.getlist('imagen')
        print(files)

        if form.is_valid():

            data = form.cleaned_data
            print(data)

            for file in files:
                img = cms_models.Imagen.objects.create(
                    titulo = data['titulo'],
                    imagen = file,
                    content_type = data['content_type'],
                    object_id = data['object_id'],
                    #content_object = data['text']
                )
            return redirect('cms:image_list')

        else:
            print(form.errors)

    else:
        form = cms_forms.ImagenForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def image_update(request, id=None):
    """
    """

    print("image update function")

    title = 'Editar Imagen'
    element = get_object_or_404(cms_models.Imagen, id=id)
    urls = getImageUrls()

    if request.method == 'POST':
        form = cms_forms.ImagenForm(request.POST, request.FILES, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:image_list')
    else:
        form = cms_forms.ImagenForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def image_view(request, id=None):
    """
    """

    print("image view function")

    title = 'Ver Imagen'
    element = get_object_or_404(cms_models.Imagen, id=id)

    list = {}
    for field in element._meta.fields:
        list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
    })


@login_required()
def image_delete(request, id=None):
    """
    """

    print("image delete function")

    title = 'Borrar Imagen'
    element = get_object_or_404(cms_models.Imagen, id=id)
    urls = getImageUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:image_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def image_filter_2(filter_dict):
    """
    """

    print("image filter 2 function")

    elements = cms_models.Imagen.objects.all()

    if filter_dict.get('text') is not None:
        elements = elements.filter(titulo__icontains=filter_dict['text'])

    if filter_dict.get('content_type') is not None:
        elements = elements.filter(content_type=filter_dict["content_type"])

    if filter_dict.get('object_id') is not None:
        elements = elements.filter(object_id=filter_dict['object_id'])

    return elements


@login_required()
def image_filter(request):
    """
    """

    print("image filter function")

    title = 'Filtrar Imagen'
    urls = getImageUrls()

    if request.method == 'POST':
        filter_dict = {}
        form = cms_forms.ImagenFilterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data.get('text') is not None:
                filter_dict['text'] = data['text']

            if data.get('content_type') is not None:
                filter_dict['content_type'] = data['content_type']

            if data.get('object_id') is not None:
                filter_dict['object_id'] = data['object_id']

            return image_list(request, filter_dict)
    else:
        form = cms_forms.ImagenFilterForm()


    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
        'urls': urls,
    })


@login_required()
def image_scrap(request):
    """
    https://stackoverflow.com/questions/6813704/how-to-download-an-image-using-selenium-any-version
    https://stackoverflow.com/questions/8286352/how-to-save-an-image-locally-using-python-whose-url-address-i-already-know
    """

    timeout = 5

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path='/Users/albertosanmartinmartinez/Downloads/chromedriver', chrome_options=option)

    browser.get('http://salamantica.com/cms/login')
    WebDriverWait(browser, timeout)

    browser.find_element_by_id("UserUsername").send_keys("rubenmartin@salamancamovil.com")
    browser.find_element_by_id("UserPassword").send_keys("D*JT3T6QDRkYc))TflBn)CH&")
    browser.find_element_by_css_selector('button[type="submit"]').click()

    # fotos de categorías

    file = open("fixtures/images_categorias.txt","w")

    browser.get('http://salamantica.com/cms/categories')
    WebDriverWait(browser, timeout)

    rows = browser.find_elements_by_tag_name('tr')

    for row in rows[1:]:
        cols = []
        [cols.append(td.text) for td in row.find_elements_by_xpath(".//td/div[@class='limitbox'][text()]")]
        images = []
        [images.append(td.get_attribute('src')) for td in row.find_elements_by_xpath(".//td/div/img[@class='img-thumbnail']")]

        list = []
        list.append(str(cols[1]))
        list.append(images)

        file.write(str(list))
        file.write(',')
        file.write('\n')

    file.close()

    # fotos de lugares

    file = open("fixtures/images_lugares.txt","w")
    url = 'http://salamantica.com/cms/places/index/page:'

    for i in range(1, 27):
        browser.get(url + str(i))
        WebDriverWait(browser, timeout)
        rows = browser.find_elements_by_tag_name('tr')

        for row in rows[1:]:
            cols = []
            [cols.append(td.text) for td in row.find_elements_by_xpath(".//td/div[@class='limitbox'][text()]")]
            images = []
            [images.append(td.get_attribute('src')) for td in row.find_elements_by_xpath(".//td/div/img[@class='img-thumbnail']")]

            list = []
            list.append(str(cols[1]))
            list.append(images)
            print(list)
            file.write(str(list))
            file.write(',')
            file.write('\n')

    file.close()

    # fotos de publicaciones

    file = open("fixtures/images_publicaciones.txt","w")
    url = 'http://salamantica.com/cms/posts/index/page:'

    for i in range(1, 4):
        browser.get(url + str(i))
        WebDriverWait(browser, timeout)
        rows = browser.find_elements_by_tag_name('tr')

        for row in rows[1:]:
            cols = []
            [cols.append(td.text) for td in row.find_elements_by_xpath(".//td/div[@class='limitbox'][text()]")]
            images = []
            [images.append(td.get_attribute('src')) for td in row.find_elements_by_xpath(".//td/div/img[@class='img-thumbnail']")]

            list = []
            list.append(str(cols[1]))
            list.append(images)
            print(list)
            file.write(str(list))
            file.write(',')
            file.write('\n')

    file.close()

    browser.close()

    return redirect('cms:image_list')


def image_upload(request):
    """
    """

    from salamantica import settings

    print("image upload function")

    host = 'http://salamantica.com/cms/files/'
    path = settings.MEDIA_ROOT

    # Categorias
    file = open("fixtures/images_categorias.txt","r")
    folder = 'category/'

    for line in file:

        aux = line.split(',')
        category = aux[0].strip("[").strip("'")
        url = aux[1].strip(" ").strip("[").strip("]").strip("'")
        file_name_extension = url.split('/')[-1]
        file_name = file_name_extension.split(".")[2]

        urllib.request.urlretrieve(host + folder + file_name_extension, path + '/photos/' + file_name + ".jpg")

        try:
            category = cms_models.Categoria.objects.get(titulo=category)
            print(category)

        except cms_models.Categoria.DoesNotExist:
            category = None
            print("not exist")

        except cms_models.Categoria.MultipleObjectsReturned:
            tmp = cms_models.Categoria.objects.filter(titulo=category.strip())
            category = tmp[0]
            print("more than one")

        try:
            image = cms_models.Imagen.objects.get_or_create(
                titulo = file_name,
                imagen = 'photos/' + file_name + '.jpg',
                content_type_id = 7,
                object_id = category.id
            )
        except cms_models.Imagen.DoesNotExist:
            print("error")

    file.close()

    # Lugares
    file = open("fixtures/images_lugares.txt","r")
    folder = 'place/'

    for line in file:

        aux = line.split(',')
        place = aux[0].strip("[").strip("'")
        url = aux[1].strip(" ").strip("[").strip("]").strip("'")
        file_name_extension = url.split('/')[-1]
        file_name = file_name_extension.split(".")[2]

        try:
            urllib.request.urlretrieve(host + folder + 'lg/' + file_name_extension, path + '/photos/' + file_name + ".jpg")
        except:
            print("not file found")

        try:
            place = cms_models.Lugar.objects.get(titulo=place)
            #print(place)

        except cms_models.Lugar.DoesNotExist:
            place = None
            #file_name = 'default'
            #place.id = 1
            print("not exist")

        except cms_models.Lugar.MultipleObjectsReturned:
            tmp = cms_models.Lugar.objects.filter(titulo=place.strip())
            place = tmp[0]
            #print("more than one")

        if place != None:
            try:
                image = cms_models.Imagen.objects.get_or_create(
                    titulo = file_name,
                    imagen = 'photos/' + file_name + '.jpg',
                    content_type_id = 9,
                    object_id = place.id
                )
            except cms_models.Imagen.DoesNotExist:
                print("error")

    file.close()

    # Publicaciones
    file = open("fixtures/images_publicaciones.txt","r")
    folder = 'posts/'
    print(folder)

    for line in file:

        aux = line.split(',')
        publication = aux[0].strip("[").strip("'")
        url = aux[1].strip(" ").strip("[").strip("]").strip("'")
        file_name_extension = url.split('/')[-1]
        file_name = file_name_extension.split(".")[2]

        #print(host + folder + file_name_extension)
        #print(path + file_name + ".jpg")

        try:
            urllib.request.urlretrieve(host + folder + file_name_extension, path + '/photos/' + file_name + ".jpg")
        except:
            print("not file found")

        try:
            publication = cms_models.Publicacion.objects.get(titulo=publication)
            print(publication)
        except cms_models.Publicacion.DoesNotExist:
            publication = None
        except cms_models.Publicacion.MultipleObjectsReturned:
            publication = None

        if publication != None:
            try:
                image = cms_models.Imagen.objects.get_or_create(
                    titulo = file_name,
                    imagen = 'photos/' + file_name + '.jpg',
                    content_type_id = 12,
                    object_id = publication.id
                )
            except cms_models.Imagen.DoesNotExist:
                print("error")

    file.close()

    return redirect('cms:image_list')


def getImageUrls():

    urls = {
        'list': 'cms:image_list',
        'create': 'cms:image_create',
        'update': 'cms:image_update',
        'view': 'cms:image_view',
        'delete': 'cms:image_delete',
        'filter': 'cms:image_filter',
        'scrap': 'cms:image_scrap',
        'upload': 'cms:image_upload',
    }

    return urls


# Video Views
@login_required()
def video_list(request, filter_dict=None):

    print("video list function")

    title = 'Videos'

    if filter_dict is None:
        filter_dict = request.GET.copy()

    if filter_dict is not None:
        if filter_dict.get('order') is not None:
            del filter_dict['order']
        if filter_dict.get('page') is not None:
            del filter_dict['page']

        elements = video_filter_2(filter_dict)

    else:
        elements = cms_models.Video.objects.all().order_by('-id')

    order = request.GET.get('order')
    if order is not None:
        elements = elements.order_by(order)
    else:
        order = '-id'

    fields = cms_models.Video._meta.fields
    urls = getVideoUrls()

    for element in elements:
        list = []
        for field in fields:
            list.append(getattr(element, field.name))
        element.fields_values = list

    paginator = Paginator(elements, 20)
    page = request.GET.get('page')

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)


    return render(request, 'list.html', {
        'elements': elements,
        'fields': fields,
        'urls': urls,
        'title': title,
        'order': order,
        'page': page,
        'filter_dict': filter_dict
    })


@login_required()
def video_create(request):

    print("video create function")

    title = 'Nuevo Video'
    urls = getVideoUrls()

    if request.method == 'POST':
        form = cms_forms.VideoForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('cms:video_list')
    else:
        form = cms_forms.VideoForm()

    return render(request, 'create.html', {
        'title': title,
        'form': form,
        'urls': urls,
    })


@login_required()
def video_update(request, id=None):

    print("video update function")

    title = 'Editar Video'
    element = get_object_or_404(cms_models.Video, id=id)
    urls = getVideoUrls()

    if request.method == 'POST':
        form = cms_forms.VideoForm(request.POST, instance=element)
        if form.is_valid():
            form.save()

            return redirect('cms:video_list')
    else:
        form = cms_forms.VideoForm(instance=element)

    return render(request, 'update.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


@login_required()
def video_view(request, id=None):

    print("video view function")

    title = 'Ver Video'
    element = get_object_or_404(cms_models.Video, id=id)

    list = {}
    for field in element._meta.fields:
        list[field.verbose_name] = getattr(element, field.name)
    element.fields_values = list

    return render(request, 'view.html', {
        'title': title,
        'element': element,
    })


@login_required()
def video_delete(request, id=None):

    print("video delete function")

    title = 'Borrar Video'
    element = get_object_or_404(cms_models.Video, id=id)
    urls = getVideoUrls()

    if request.method == 'POST':
        form = cms_forms.ConfirmationForm(request.POST)
        if form.is_valid():
            element.delete()

            return redirect('cms:video_list')
    else:
        form = cms_forms.ConfirmationForm()

    return render(request, 'delete.html', {
        'title': title,
        'element': element,
        'form': form,
        'urls': urls,
    })


def video_filter_2(filter_dict):
    """
    """

    print("video filter 2 function")

    elements = cms_models.Video.objects.all()

    if filter_dict.get('text') is not None:
        elements = elements.filter(titulo__icontains=filter_dict['text'])

    if filter_dict.get('content_type') is not None:
        elements = elements.filter(content_type=filter_dict["content_type"])

    if filter_dict.get('object_id') is not None:
        elements = elements.filter(created_date__gte=filter_dict['object_id'])

    return elements


@login_required()
def video_filter(request):

    print("video filter function")

    title = 'Filtrar Video'
    urls = getVideoUrls()

    if request.method == 'POST':
        filter_dict = {}
        form = cms_forms.VideoFilterForm(request.POST)
        if form.is_valid():

            if filter_dict.get('text') is not None:
                elements = elements.filter(titulo=filter_dict['text'])

            return video_list(request, filter_dict)
    else:
        form = cms_forms.VideoFilterForm()


    return render(request, 'filter.html', {
        'title': title,
        'urls': urls,
        'form': form,
        'urls': urls,
    })


def video_scrap(request):
    pass


def video_upload(request):
    pass


def getVideoUrls():

    urls = {
        'list': 'cms:video_list',
        'create': 'cms:video_create',
        'update': 'cms:video_update',
        'view': 'cms:video_view',
        'delete': 'cms:video_delete',
        'filter': 'cms:video_filter',
        'scrap': 'cms:video_scrap',
        'upload': 'cms:video_upload',
    }

    return urls


# Handler Views
def handler400(request, exception, template_name='400.html'):
    """
    """

    response = render_to_response("400.html")
    response.status_code = 400
    return response


def handler403(request, exception, template_name='403.html'):
    """
    """

    response = render_to_response("403.html")
    response.status_code = 403
    return response


def handler404(request, exception, template_name='404.html'):
    """
    """

    response = render_to_response("404.html")
    response.status_code = 404
    return response


def handler500(request, exception, template_name='500.html'):
    """
    """

    response = render_to_response("500.html")
    response.status_code = 500
    return response




# API Views
@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def rest_category_list(request):
    """
    """

    print("catergory list api function")

    parent_category_id = request.GET.get('parent_category_id')

    if parent_category_id == 'null':
        print("parent category id null")
        elements = cms_models.Categoria.objects.filter(categoria_padre_id=None, estado='Activo') #.order_by('id')
    else:
        print("parent category id not null")
        elements = cms_models.Categoria.objects.filter(categoria_padre_id=parent_category_id, estado='Activo')#.prefetch_related('places') #.order_by('id')

    elements = cms_serializers.CategorySerializer(elements, context={"request": request}, many=True)

    return Response(elements.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def rest_category_detail(request):
    """
    """

    print("catergory detail api function")

    category_id = request.GET.get('category_id')
    serialized_element = None

    if category_id != 'null':
        print("category id not null")
        element = get_object_or_404(cms_models.Categoria, id=category_id)
        serialized_element = cms_serializers.CategorySerializer(element, context={"request": request})

    return Response(serialized_element.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def rest_category_final(request):
    """
    """

    print('modal categories final api function')

    elements = cms_models.Categoria.objects.filter(child_category__isnull=True, estado='Activo')
    serialized_elements = cms_serializers.CategorySerializer(elements, context={"request": request}, many=True)

    return Response(serialized_elements.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def rest_place_list(request):
    """
    """

    print("places list api function")

    place_id = None
    place_id = request.GET.get('place_id')
    category_id = None
    category_id = request.GET.get('category_id')
    print(category_id)

    if place_id != None:
        print("place not none")
        element = get_object_or_404(cms_models.Lugar, id=place_id)
        element = cms_serializers.PlaceSerializer(element, context={"request": request})

        return Response(element.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)

    else:
        if category_id == 'undefined':
            elements = cms_models.Lugar.objects.filter(estado='Activo').order_by('destacado', 'prioridad')
        else:
            elements = cms_models.Lugar.objects.filter(categoria_id=category_id, estado='Activo').order_by('destacado', 'prioridad')

    elements = cms_serializers.PlaceSerializer(elements, context={"request": request}, many=True)

    return Response(elements.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def rest_promo_list(request):
    """
    """

    print("promo list api function")

    promo_id = request.GET.get('promo_id')
    print(promo_id)
    place_id = request.GET.get('place_id')
    print(place_id)

    if promo_id != None:
        print("promo id not none")
        element = get_object_or_404(cms_models.Promo, id=promo_id)
        element = cms_serializers.PromoSerializer(element, context={"request": request})

        return Response(element.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)

    else:
        print("promo id none")
        if place_id is 'null':
            print("place id none")
            elements = cms_models.Promo.objects.filter(estado='Activo').order_by('-created_date')
        else:
            print("place id not none")
            elements = cms_models.Promo.objects.filter(lugar_id=place_id, estado='Activo').order_by('-created_date')

    elements = cms_serializers.PromoSerializer(elements, context={"request": request}, many=True)

    return Response(elements.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def rest_event_list(request):
    """
    """

    print("events api function")

    event_id = request.GET.get('event_id')
    print(event_id)

    if event_id is None:
        elements = cms_models.Publicacion.objects.filter(estado='Activo', tipo='Evento').order_by('-created_date')
        elements = cms_serializers.PublicationSerializer(elements, context={"request": request}, many=True)
    else:
        elements = get_object_or_404(cms_models.Publicacion, id=event_id)
        elements = cms_serializers.PublicationSerializer(elements, context={"request": request})

    return Response(elements.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def rest_new_list(request):
    """
    """

    print("news api function")

    new_id = request.GET.get('new_id')
    print(new_id)

    if new_id is None:
        elements = cms_models.Publicacion.objects.filter(estado='Activo', tipo='Noticia').order_by('-created_date')
        elements = cms_serializers.PublicationSerializer(elements, context={"request": request}, many=True)
    else:
        elements = get_object_or_404(cms_models.Publicacion, id=new_id)
        elements = cms_serializers.PublicationSerializer(elements, context={"request": request})

    return Response(elements.data, status=status.HTTP_200_OK, template_name=None, headers=None, content_type=None)




#

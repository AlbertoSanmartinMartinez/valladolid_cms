
#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelformset_factory


from cms import models as cms_models


# General Forms
class LoginForm(AuthenticationForm):
    """
    """

    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': u'Nombre de Usuario o correo electrónico'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': u'Contraseña'}))


class SingupForm(forms.Form):
    """
    """
    username = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder':'Nombre de usuario'}))
    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'placeholder': u'Correo electrónico'}))
    first_name = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'placeholder':'Nombre'}))
    last_name = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'placeholder':'Apellidos'}))
    #password1 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': u'Contraseña'}))
    #password2 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': u'Confirmar contraseña'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ResetForm(forms.Form):
    """
    """
    username = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder':'Nombre de usuario o correo electrónico'}))


class ResetPasswordForm(forms.Form):
    """
    """

    username = forms.CharField(label="", widget=forms.HiddenInput)
    password1 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': u'Contraseña'}))
    password2 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': u'Confirmar contraseña'}))


# CMS Forms
class EntidadForm(forms.Form):
    """
    category filter
    start_date & end_date forced this names
    https://reviblog.net/2014/01/07/jquery-ui-datepicker-poner-el-calendario-en-espanol-euskera-o-cualquier-otro-idioma/
    """

    text = forms.CharField(label='Texto', required=False, widget=forms.TextInput(attrs={'placeholder': 'Buscar'}))
    STATUS = (("Activo", "Activo"), ("Inactivo", "Inactivo"))
    status = forms.ChoiceField(label='Tipo', required=False, choices=STATUS)
    start_date = forms.DateField(label='Fecha Inicio', required=False, widget=forms.TextInput(attrs={'placeholder': '31/12/20019', 'class': 'datepicker'}))
    end_date = forms.DateField(label='Fecha Fin', required=False, widget=forms.TextInput(attrs={'placeholder': '31/12/20019', 'class': 'datepicker'}))
    start_priority = forms.IntegerField(label='Prioridad Mínima', required=False, widget=forms.TextInput(attrs={'placeholder': '-10'}))
    end_priority = forms.IntegerField(label='Prioridad Máxima', required=False, widget=forms.TextInput(attrs={'placeholder': '10'}))


class CategoryForm(forms.ModelForm):
    """
    """

    class Meta:
        model = cms_models.Categoria
        fields = '__all__'


class CategoryFilterForm(EntidadForm):
    """
    """

    def __init__(self, *args, **kwargs):
        super(CategoryFilterForm, self).__init__(*args, **kwargs)
        self.fields['categoria_padre'] = forms.ModelChoiceField(
            label='Categoría Padre',
            required=False,
            queryset=cms_models.Categoria.objects.all().order_by('titulo'))


class PlaceForm(forms.ModelForm):

    class Meta:
        model = cms_models.Lugar
        fields = '__all__'


class PlaceFilterForm(EntidadForm):
    """
    """

    start_rank = forms.IntegerField(label='Puntuación Mínima', required=False, widget=forms.TextInput(attrs={'placeholder': '0'}))
    end_rank = forms.IntegerField(label='Puntuación Máxima', required=False, widget=forms.TextInput(attrs={'placeholder': '5'}))
    destacado = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(PlaceFilterForm, self).__init__(*args, **kwargs)
        self.fields['categoria'] = forms.ModelChoiceField(
            label='Categoría',
            required=False,
            queryset=cms_models.Categoria.objects.all().order_by('titulo'))



class PublicacionForm(forms.ModelForm):

    class Meta:
        model = cms_models.Publicacion
        fields = '__all__'


class PublicacionFilterForm(EntidadForm):
    """
    """

    TIPO = (("Noticia", "Noticia"), ("Evento", "Evento"))
    type = forms.ChoiceField(label='Tipo', required=False, choices=TIPO)

    def __init__(self, *args, **kwargs):
        super(PublicacionFilterForm, self).__init__(*args, **kwargs)
        self.fields['categoria'] = forms.ModelChoiceField(
            label='Categoría',
            required=False,
            queryset=cms_models.Categoria.objects.all().order_by('titulo'))


class PromoForm(forms.ModelForm):

    class Meta:
        model = cms_models.Promo
        fields = '__all__'


class PromoFilterForm(EntidadForm):
    """
    """

    def __init__(self, *args, **kwargs):
        super(PromoFilterForm, self).__init__(*args, **kwargs)
        self.fields['place'] = forms.ModelChoiceField(
            label='Lugar',
            required=False,
            queryset=cms_models.Lugar.objects.all().order_by('titulo'))


class PrecioForm(forms.ModelForm):

    class Meta:
        model = cms_models.Precio
        fields = '__all__'


class PrecioFilterForm(EntidadForm):
    """
    """

    start_price = forms.DecimalField(label='Cantidad Mínimo', required=False, widget=forms.TextInput(attrs={'placeholder': '10'}))
    end_price = forms.DecimalField(label='Cantidad Máximo', required=False, widget=forms.TextInput(attrs={'placeholder': '10'}))

    def __init__(self, *args, **kwargs):
        super(PrecioFilterForm, self).__init__(*args, **kwargs)
        self.fields['place'] = forms.ModelChoiceField(
            label='Lugar',
            required=False,
            queryset=cms_models.Lugar.objects.all())


class HorarioForm(forms.ModelForm):

    class Meta:
        model = cms_models.Horario
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(HorarioForm, self).__init__(*args, **kwargs)
        self.fields['lugar'] = forms.ModelChoiceField(
            label='Lugar',
            required=True,
            queryset=cms_models.Lugar.objects.all().order_by('titulo'))


class HorarioFilterForm(EntidadForm):
    """
    """

    def __init__(self, *args, **kwargs):
        super(HorarioFilterForm, self).__init__(*args, **kwargs)
        self.fields['place'] = forms.ModelChoiceField(
            label='Lugar',
            required=False,
            queryset=cms_models.Lugar.objects.all().order_by('titulo'))


class PeriodoHorarioForm(forms.ModelForm):

    inicio = forms.TimeField(label='Apertura', required=True, widget=forms.TextInput(attrs={'placeholder': '09:00'}))
    fin = forms.TimeField(label='Cierre', required=True, widget=forms.TextInput(attrs={'placeholder': '20:00'}))

    class Meta:
        model = cms_models.PeriodoHorario
        fields = '__all__'


PeriodoHorarioFormset = modelformset_factory(
    cms_models.PeriodoHorario,
    #extra=1,
    #can_delete=True,
    #can_order=True
    #fields=('dia', 'inicio', 'fin'),
    #form=PeriodoHorarioForm
    exclude=('horario',)
)

"""
class PeriodoHorarioFormset(BasePeriodoHorarioFormset):

    def __init__(self, *args, **kwargs):
        super(PeriodoHorarioFormset, self).__init__(*args, **kwargs)
        print(kwargs.get('extra', None))

        self.fields['extra'] = extra
"""

class ImagenForm(forms.ModelForm):
    """
    """

    imagen = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple':True}))

    class Meta:
        model = cms_models.Imagen
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        print("image form function")
        super(ImagenForm, self).__init__(*args, **kwargs)
        models_list = ['categoria', 'lugar', 'promo', 'publicacion']
        self.fields['content_type'] = forms.ModelChoiceField(
            label='Tipo',
            queryset=ContentType.objects.filter(app_label='cms', model__in=models_list))
        """
        self.fields['imagen'] = forms.FileField(
            widget=forms.ClearableFileInput(
                attrs={'multiple': True}
            )
        )
        """


class ImagenFilterForm(forms.ModelForm):
    """
    """

    text = forms.CharField(label='Texto', required=False, widget=forms.TextInput(attrs={'placeholder': 'Buscar'}))

    class Meta:
        model = cms_models.Imagen
        fields = ['text', 'content_type', 'object_id']

    def __init__(self, *args, **kwargs):
        super(ImagenFilterForm, self).__init__(*args, **kwargs)
        models_list = ['categoria', 'lugar', 'promo', 'publicacion']
        self.fields['content_type'] = forms.ModelChoiceField(
            label='Tipo',
            queryset=ContentType.objects.filter(app_label='cms', model__in=models_list))


class VideoForm(forms.ModelForm):

    class Meta:
        model = cms_models.Video
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        print("video form function")
        super(VideoForm, self).__init__(*args, **kwargs)
        models_list = ['categoria', 'lugar', 'promo', 'publicacion']
        self.fields['content_type'] = forms.ModelChoiceField(
            label='Tipo',
            queryset=ContentType.objects.filter(app_label='cms', model__in=models_list))


class VideoFilterForm(forms.ModelForm):
    """
    """

    text = forms.CharField(label='Texto', required=False, widget=forms.TextInput(attrs={'placeholder': 'Buscar'}))

    class Meta:
        model = cms_models.Video
        fields = ['text', 'content_type', 'object_id']

    def __init__(self, *args, **kwargs):
        super(VideoFilterForm, self).__init__(*args, **kwargs)
        models_list = ['categoria', 'lugar', 'promo', 'publicacion']
        self.fields['content_type'] = forms.ModelChoiceField(
            label='Tipo',
            queryset=ContentType.objects.filter(app_label='cms', model__in=models_list))


class UserForm(forms.ModelForm):
    """
    """

    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'is_staff', 'groups', 'user_permissions', 'last_login', 'date_joined')


class ConfirmationForm(forms.Form):
    """
    """

    ok = forms.IntegerField(widget=forms.HiddenInput(), initial=1, label='')




#

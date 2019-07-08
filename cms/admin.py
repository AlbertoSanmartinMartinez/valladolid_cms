
#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
https://docs.djangoproject.com/es/2.1/ref/contrib/admin/
"""

from django.contrib import admin

from cms import models


# Register your models here.
class CategoriaAdmin(admin.ModelAdmin):
    """
    """

    list_display = ('id', 'estado', 'categoria_padre', 'titulo', 'subtitulo', 'informacion', 'prioridad', 'color')
    list_filter = ('categoria_padre', )
    search_fields = ('titulo', 'subtitulo', 'informacion')
    list_editable = ('estado', 'categoria_padre', 'titulo', 'subtitulo', 'prioridad', 'color')

admin.site.register(models.Categoria, CategoriaAdmin)


class LugarAdmin(admin.ModelAdmin):
    """
    """

    list_display = ('id', 'estado', 'categoria', 'titulo', 'subtitulo', 'informacion', 'prioridad', 'puntuacion', 'destacado', 'servicios')
    list_filter = ('categoria', 'estado', 'destacado')
    search_fields = ('titulo', 'subtitulo', 'informacion')
    list_editable = ('estado', 'categoria', 'titulo', 'subtitulo', 'prioridad', 'puntuacion', 'destacado')

admin.site.register(models.Lugar, LugarAdmin)

admin.site.register(models.Publicacion)


class PromoAdmin(admin.ModelAdmin):
    """
    """

    list_display = ('id', 'estado', 'lugar', 'titulo', 'subtitulo', 'informacion', 'prioridad')
    list_filter = ('estado', )
    search_fields = ('titulo', 'subtitulo', 'informacion')

admin.site.register(models.Promo, PromoAdmin)

admin.site.register(models.Precio)

admin.site.register(models.Horario)

admin.site.register(models.PeriodoHorario)

#admin.site.register(models.DiaHorario)

admin.site.register(models.Imagen)

admin.site.register(models.Video)

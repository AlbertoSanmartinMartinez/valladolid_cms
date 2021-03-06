# Generated by Django 2.2.3 on 2019-07-08 13:11

import ckeditor.fields
import cms.models
from django.db import migrations, models
import django.db.models.deletion
import embed_video.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default=1, max_length=20, verbose_name='Estado')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('en_titulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Título')),
                ('subtitulo', models.CharField(blank=True, max_length=100, verbose_name='Subtítulo')),
                ('en_subtitulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Subtítulo')),
                ('informacion', ckeditor.fields.RichTextField(blank=True, verbose_name='Información')),
                ('en_informacion', ckeditor.fields.RichTextField(blank=True, default='', verbose_name='En Información')),
                ('prioridad', cms.models.IntegerRangeField(blank=True, null=True, verbose_name='Prioridad')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')),
                ('color', models.CharField(blank=True, max_length=7, null=True, verbose_name='Color')),
                ('categoria_padre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_category', related_query_name='child_category', to='cms.Categoria', verbose_name='Categoría Padre')),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
            },
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default=1, max_length=20, verbose_name='Estado')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('en_titulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Título')),
                ('subtitulo', models.CharField(blank=True, max_length=100, verbose_name='Subtítulo')),
                ('en_subtitulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Subtítulo')),
                ('informacion', ckeditor.fields.RichTextField(blank=True, verbose_name='Información')),
                ('en_informacion', ckeditor.fields.RichTextField(blank=True, default='', verbose_name='En Información')),
                ('prioridad', cms.models.IntegerRangeField(blank=True, null=True, verbose_name='Prioridad')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')),
            ],
            options={
                'verbose_name': 'Horario',
                'verbose_name_plural': 'Horarios',
            },
        ),
        migrations.CreateModel(
            name='Lugar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default=1, max_length=20, verbose_name='Estado')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('en_titulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Título')),
                ('subtitulo', models.CharField(blank=True, max_length=100, verbose_name='Subtítulo')),
                ('en_subtitulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Subtítulo')),
                ('informacion', ckeditor.fields.RichTextField(blank=True, verbose_name='Información')),
                ('en_informacion', ckeditor.fields.RichTextField(blank=True, default='', verbose_name='En Información')),
                ('prioridad', cms.models.IntegerRangeField(blank=True, null=True, verbose_name='Prioridad')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')),
                ('puntuacion', cms.models.IntegerRangeField(blank=True, null=True, verbose_name='Puntuación')),
                ('destacado', models.BooleanField(blank=True, default=False, verbose_name='Destacado')),
                ('servicios', models.TextField(blank=True, default='', verbose_name='Servicios')),
                ('en_servicios', models.TextField(blank=True, default='', verbose_name='En Servicios')),
                ('latitud', models.CharField(blank=True, max_length=20, null=True, verbose_name='Latitud')),
                ('longitud', models.CharField(blank=True, max_length=20, null=True, verbose_name='Longitud')),
                ('telefono1', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono 1')),
                ('telefono2', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono 2')),
                ('url', models.URLField(blank=True, null=True, verbose_name='Pagina Web')),
                ('reserva', models.URLField(blank=True, null=True, verbose_name='Reservar')),
                ('compra', models.URLField(blank=True, null=True, verbose_name='Comprar')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('vista360', models.URLField(blank=True, null=True, verbose_name='Vista 360')),
                ('facebook', models.URLField(blank=True, null=True, verbose_name='Facebook')),
                ('twitter', models.URLField(blank=True, null=True, verbose_name='Twitter')),
                ('instagram', models.URLField(blank=True, null=True, verbose_name='Instagram')),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='place_category', to='cms.Categoria', verbose_name='Categoria')),
            ],
            options={
                'verbose_name': 'Lugar',
                'verbose_name_plural': 'Lugares',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('video', embed_video.fields.EmbedVideoField(verbose_name='Video Url')),
                ('object_id', models.PositiveIntegerField(default=1, verbose_name='Objeto')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_type_video', to='contenttypes.ContentType', verbose_name='Tipo')),
            ],
            options={
                'verbose_name': 'Video',
                'verbose_name_plural': 'Videos',
            },
        ),
        migrations.CreateModel(
            name='Publicacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default=1, max_length=20, verbose_name='Estado')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('en_titulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Título')),
                ('subtitulo', models.CharField(blank=True, max_length=100, verbose_name='Subtítulo')),
                ('en_subtitulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Subtítulo')),
                ('informacion', ckeditor.fields.RichTextField(blank=True, verbose_name='Información')),
                ('en_informacion', ckeditor.fields.RichTextField(blank=True, default='', verbose_name='En Información')),
                ('prioridad', cms.models.IntegerRangeField(blank=True, null=True, verbose_name='Prioridad')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')),
                ('tipo', models.CharField(choices=[('Noticia', 'Noticia'), ('Evento', 'Evento')], default=1, max_length=20, verbose_name='Tipo')),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publication_category', to='cms.Categoria', verbose_name='Categoría')),
            ],
            options={
                'verbose_name': 'Publicacion',
                'verbose_name_plural': 'Publicaciones',
            },
        ),
        migrations.CreateModel(
            name='Promo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default=1, max_length=20, verbose_name='Estado')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('en_titulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Título')),
                ('subtitulo', models.CharField(blank=True, max_length=100, verbose_name='Subtítulo')),
                ('en_subtitulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Subtítulo')),
                ('informacion', ckeditor.fields.RichTextField(blank=True, verbose_name='Información')),
                ('en_informacion', ckeditor.fields.RichTextField(blank=True, default='', verbose_name='En Información')),
                ('prioridad', cms.models.IntegerRangeField(blank=True, null=True, verbose_name='Prioridad')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')),
                ('lugar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='promo_place', to='cms.Lugar', verbose_name='Lugar')),
            ],
            options={
                'verbose_name': 'Promo',
                'verbose_name_plural': 'Promos',
            },
        ),
        migrations.CreateModel(
            name='Precio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default=1, max_length=20, verbose_name='Estado')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('en_titulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Título')),
                ('subtitulo', models.CharField(blank=True, max_length=100, verbose_name='Subtítulo')),
                ('en_subtitulo', models.CharField(blank=True, default='', max_length=100, verbose_name='En Subtítulo')),
                ('informacion', ckeditor.fields.RichTextField(blank=True, verbose_name='Información')),
                ('en_informacion', ckeditor.fields.RichTextField(blank=True, default='', verbose_name='En Información')),
                ('prioridad', cms.models.IntegerRangeField(blank=True, null=True, verbose_name='Prioridad')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')),
                ('cantidad', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Cantidad')),
                ('lugar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='price_place', to='cms.Lugar', verbose_name='Lugar')),
            ],
            options={
                'verbose_name': 'Precio',
                'verbose_name_plural': 'Precios',
            },
        ),
        migrations.CreateModel(
            name='PeriodoHorario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.CharField(blank=True, choices=[('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miercoles', 'Miercoles'), ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')], default='Lunes', max_length=9, verbose_name='Día')),
                ('inicio', models.TimeField(default='09:00', verbose_name='Apertura')),
                ('fin', models.TimeField(default='20:00', verbose_name='Cierre')),
                ('horario', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='schedule_periods', to='cms.Horario', verbose_name='Horario')),
            ],
            options={
                'verbose_name': 'Periodo Horario',
                'verbose_name_plural': 'Periodos Horario',
            },
        ),
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('header', models.BooleanField(default=False, verbose_name='Principal')),
                ('imagen', models.ImageField(default='photos/default.jpg', upload_to='photos', verbose_name='Imagen')),
                ('object_id', models.PositiveIntegerField(default=1, verbose_name='Objeto')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_type_image', to='contenttypes.ContentType', verbose_name='Tipo')),
            ],
            options={
                'verbose_name': 'Imagen',
                'verbose_name_plural': 'Imagenes',
            },
        ),
        migrations.AddField(
            model_name='horario',
            name='lugar',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schedule_place', to='cms.Lugar', verbose_name='Lugar'),
        ),
    ]


#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from rest_framework import serializers

from cms import models as cms_models


# Serializers
class VideoSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = cms_models.Video
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    """
    """

    imagen = serializers.SerializerMethodField()

    class Meta:
        model = cms_models.Imagen
        fields = '__all__'

    def get_imagen(self, obj):
        """
        mthod to get full image url ip server + path + file name
        """
        request = self.context.get('request')
        photo_url = obj.imagen.url

        return request.build_absolute_uri(photo_url)


class SchedulePeriodSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = cms_models.PeriodoHorario
        fields = '__all__'


class PriceSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = cms_models.Precio
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    """
    """

    schedule_periods = SchedulePeriodSerializer(many=True)

    class Meta:
        model = cms_models.Horario
        fields = '__all__'


class PromoSerializer(serializers.ModelSerializer):
    """
    """

    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = cms_models.Promo
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    """
    """

    images = ImageSerializer(many=True, read_only=True)
    schedule_place = ScheduleSerializer(many=True)
    price_place = PriceSerializer(many=True)
    promo_place = PromoSerializer(many=True)
    #informacion = SerializerMethodField(informationSerializer)
    informacion = serializers.ReadOnlyField()#source='informationHtmlSafe')

    class Meta:
        model = cms_models.Lugar
        fields = '__all__'
    """
    def informationSerializer(self, obj):

        return self.
    """

class CategorySerializer(serializers.ModelSerializer):
    """
    """

    place_category = PlaceSerializer(many=True)
    #publication_category = PublicationSerializer(many=True)
    images = ImageSerializer(many=True, read_only=True)
    parent_category = serializers.StringRelatedField(many=True)

    class Meta:
        model = cms_models.Categoria
        fields = '__all__'
        #exclude = ('categoria_padre',)
        #depth = 1


class PublicationSerializer(serializers.ModelSerializer):
    """
    """

    images = ImageSerializer(many=True, read_only=True)
    categoria = CategorySerializer(read_only=True)

    class Meta:
        model = cms_models.Publicacion
        fields = '__all__'




#

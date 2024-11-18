import base64

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from address_app.serializers import CitySerializer
from .models import Promotion, PromoCategory, Participation


class PromoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCategory
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}, 'name': {'read_only': True}}


class PromotionSerializer(serializers.ModelSerializer):
    volunteers_count = serializers.SerializerMethodField()
    category = PromoCategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    address = serializers.CharField(max_length=255, allow_blank=True, required=False)
    contact_person = serializers.PrimaryKeyRelatedField(read_only=True)
    picture64 = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        # fields = '__all__'
        exclude = ['users', 'picture']
        extra_kwargs = {
            'id': {'read_only': True},
            'quantity': {'read_only': True},
            'available_quantity': {'read_only': True},
            'volunteers_count': {'read_only': True},
        }

    # Подсчет числа участников поощрений
    def get_volunteers_count(self, obj):
        return Participation.objects.filter(promotion=obj).count()

    def get_picture64(self, obj):
        if obj.picture:
            with open(obj.picture.path, 'rb') as img:
                decoded = base64.b64encode(img.read()).decode('utf-8')
            return decoded
        else:
            return None


class ParticipationSerializer(serializers.ModelSerializer):
    promotion_id = serializers.IntegerField()
    tg_id = serializers.IntegerField()

    class Meta:
        model = Participation
        fields = ['promotion_id', 'tg_id']

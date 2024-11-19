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

    class Meta:
        model = Promotion
        # fields = '__all__'
        exclude = ['users']
        extra_kwargs = {
            'id': {'read_only': True},
            'quantity': {'read_only': True},
            'available_quantity': {'read_only': True},
            'volunteers_count': {'read_only': True},
        }

    # Подсчет числа участников поощрений
    def get_volunteers_count(self, obj):
        return Participation.objects.filter(promotion=obj).count()
      

class ParticipationSerializer(serializers.ModelSerializer):
    promotion_id = serializers.IntegerField()
    tg_id = serializers.IntegerField()

    class Meta:
        model = Participation
        fields = ['promotion_id', 'tg_id']

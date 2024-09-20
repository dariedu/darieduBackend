from rest_framework import serializers
from address_app.serializers import CitySerializer
from .models import Promotion, PromoCategory


class PromoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCategory
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}, 'name': {'read_only': True}}


class PromotionSerializer(serializers.ModelSerializer):
    volunteers_count = serializers.SerializerMethodField()
    category = PromoCategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = Promotion
        # fields = '__all__'
        exclude = ['users']
        extra_kwargs = {
            'id': {'read_only': True},
            'quantity': {'read_only': True},
            'available_quantity': {'read_only': True},
            'users': {'read_only': True},  # Список пользователей будет меняться через модель 'Participation'
        }

    # Подсчет числа участников поощрений
    def get_volunteers_count(self, obj):
        return obj.volunteers_count()

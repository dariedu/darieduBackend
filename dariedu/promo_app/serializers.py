from rest_framework import serializers
from .models import Promotion


class PromotionSerializer(serializers.ModelSerializer):
    volunteers_count = serializers.SerializerMethodField()

    # TODO we need here only GET and UPDATE to take the promotion
    class Meta:
        model = Promotion
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'quantity': {'read_only': True},
            'available_quantity': {'read_only': True},
            'users': {'read_only': True},  # Список пользователей будет меняться через модель 'Participation'
        }

    # Подсчет числа участников поощрений
    def get_volunteers_count(self, obj):
        return obj.volunteers_count()

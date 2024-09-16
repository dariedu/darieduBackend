from rest_framework import serializers

from .models import User, Rating


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('tg_id', 'email', 'last_name', 'name', 'surname', 'phone', 'is_adult', 'consent_to_personal_data')

class TelegramDataSerializer(serializers.Serializer):
    tg_id = serializers.IntegerField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'tg_id': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'volunteer_hour': {'read_only': True},
            'rating': {'read_only': True},
        }


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }

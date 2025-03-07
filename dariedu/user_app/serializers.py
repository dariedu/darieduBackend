from django.contrib.auth import get_user_model

from rest_framework import serializers

from address_app.serializers import CitySerializer
from .models import Rating
from address_app.models import City

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'tg_id',
            'tg_username',
            'email',
            'last_name',
            'name',
            'surname',
            'phone',
            'photo',
            'photo_view',
            'birthday',
            'is_adult',
            'city',
            'consent_to_personal_data'
        )
        read_only_fields = ('photo_view',)


class TelegramDataSerializer(serializers.Serializer):
    tg_id = serializers.IntegerField()


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'level': {'read_only': True},
            'hours_needed': {'read_only': True},
        }


class UserSerializer(serializers.ModelSerializer):
    rating = RatingSerializer(read_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'tg_id',
            'tg_username',
            'email',
            'last_name',
            'name',
            'surname',
            'phone',
            'photo',
            'photo_view',
            'birthday',
            'is_adult',
            'is_confirmed',  # confirmed
            'volunteer_hour',
            'point',
            'rating',
            'city',
            'is_superuser',
            'is_staff',
            'metier',
            'interests',
            'consent_to_personal_data'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'tg_id': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'volunteer_hour': {'read_only': True},
            'rating': {'read_only': True},
            'is_confirmed': {'read_only': True}  # Только для чтения
        }

        def update(self, instance, validated_data):

            instance.email = validated_data.get('email', instance.email)
            instance.photo = validated_data.get('photo', instance.photo)
            instance.phone = validated_data.get('phone', instance.phone)
            instance.city = validated_data.get('city', instance.city)
            instance.interests = validated_data.get('interests', instance.interests)
            instance.consent_to_personal_data = validated_data.get('consent_to_personal_data',
                                                                   instance.consent_to_personal_data)

            instance.save()
            return instance

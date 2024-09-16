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
        fields = [
            'id',
            'tg_id',
            'email',
            'last_name',
            'name',
            'surname',
            'phone',
            'photo',
            'volunteer_hour',
            'point',
            'rating',
            'city',
            'is_superuser',
            'is_staff',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'tg_id': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'volunteer_hour': {'read_only': True},
            'rating': {'read_only': True},
        }

        def update(self, instance, validated_data):
            instance.email = validated_data.get('email', instance.email)
            instance.photo = validated_data.get('photo', instance.photo)
            instance.city = validated_data.get('city', instance.city)

            if any([
                instance.last_name != validated_data.get('last_name', instance.last_name),
                instance.name != validated_data.get('name', instance.name),
                instance.surname != validated_data.get('surname', instance.surname),
                instance.phone != validated_data.get('phone', instance.phone)
            ]):
                raise serializers.ValidationError('Поьзовательские данные не могут быть изменены')
            instance.save()
            return instance


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'level': {'read_only': True},
            'hours_needed': {'read_only': True},
        }

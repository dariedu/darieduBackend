from rest_framework import serializers

from .models import User, Rating


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('tg_id', 'email', 'password', 'last_name', 'name', 'surname', 'phone')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    tg_id = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True, write_only=True)

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

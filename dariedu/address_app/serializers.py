from rest_framework import serializers

from user_app.models import User
from .models import Address, Location, City, RouteSheet, Beneficiar


class BeneficiarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiar
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class CuratorSerializer(serializers.ModelSerializer):
    """To show curators data"""
    class Meta:
        model = User
        fields = [
            'id',
            'tg_id',
            'tg_username',
            'last_name',
            'name',
            'surname',
            'phone',
            'photo',
            'avatar',
        ]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class AddressSerializer(serializers.ModelSerializer):
    beneficiar = BeneficiarSerializer(many=True, read_only=True)
    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class LocationSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    curator = CuratorSerializer(read_only=True)
    class Meta:
        model = Location
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class RouteSheetSerializer(serializers.ModelSerializer):
    # TODO we should promote some logic here
    location = LocationSerializer(read_only=True)
    address = AddressSerializer(many=True, read_only=True)
    class Meta:
        model = RouteSheet
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }

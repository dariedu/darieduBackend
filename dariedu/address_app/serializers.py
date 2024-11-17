from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Address, Location, City, RouteSheet, Beneficiar, RouteAssignment

User = get_user_model()


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
            'photo_view',
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


class RouteAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteAssignment
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }
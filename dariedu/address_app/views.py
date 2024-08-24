from django.shortcuts import render
from rest_framework import viewsets

from .models import Address, Location, City, RouteSheet, Beneficiar
from .serializers import (
    AddressSerializer,
    LocationSerializer,
    CitySerializer,
    RouteSheetSerializer,
    BeneficiarSerializer
)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filterset_fields = [
        'location__city',
        'location',
        'route_sheet',
        'location__curator'
    ]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filterset_fields = [
        'city',
        'curator',
        # 'route_sheet__delivery__is_active',
        # 'route_sheet__delivery__is_free'
    ]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class RouteSheetViewSet(viewsets.ModelViewSet):
    queryset = RouteSheet.objects.all()
    serializer_class = RouteSheetSerializer
    filterset_fields = [
        'delivery__is_active',
        'delivery__is_free',
        # 'location',  #TODO do not work
    ]


class BeneficiarViewSet(viewsets.ModelViewSet):
    queryset = Beneficiar.objects.all()
    serializer_class = BeneficiarSerializer
    filterset_fields = ['address', 'address__location']

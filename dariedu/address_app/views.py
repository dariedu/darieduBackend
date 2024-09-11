from django.shortcuts import render
from rest_framework import viewsets, mixins

from .models import Address, Location, City, RouteSheet, Beneficiar
from .serializers import (
    AddressSerializer,
    LocationSerializer,
    CitySerializer,
    RouteSheetSerializer,
    BeneficiarSerializer
)


class AddressViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = [
        'location__city',
        'location',
        'route_sheet',
        'location__curator'
    ]


class LocationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = [
        'city',
        'curator',
    ]


class CityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready


class RouteSheetViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = RouteSheet.objects.all()
    serializer_class = RouteSheetSerializer
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready
    filterset_fields = [
        'delivery__is_active',
        'delivery__is_free',
        # 'location',  #TODO do not work
    ]


class BeneficiarViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Beneficiar.objects.all()
    serializer_class = BeneficiarSerializer
    filterset_fields = ['address', 'address__location']
    # permission_classes = [IsAuthenticated]  # TODO swap to comment when authentication is ready


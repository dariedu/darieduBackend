from django.shortcuts import render
from rest_framework import viewsets

from .models import Address, Location, City, RouteSheet, Beneficiar


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = Address
    filter_fields = ['location__city', 'location', 'route_sheet', 'location__curator']
    search_fields = ['address', 'beneficiar', 'location']


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = Location
    filter_fields = ['city', 'curator', 'route_sheet__delivery__is_active', 'route_sheet__delivery__is_free']
    search_fields = ['address', 'adress_location', 'beneficiar', 'curator']


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = City


class RouteSheetViewSet(viewsets.ModelViewSet):
    queryset = RouteSheet.objects.all()
    serializer_class = RouteSheet
    filter_fields = ['delivery__is_active', 'delivery__is_free', 'location']
    search_fields = ['address_route_sheet', 'location__beneficiar']


class BeneficiarViewSet(viewsets.ModelViewSet):
    queryset = Beneficiar.objects.all()
    serializer_class = Beneficiar
    filter_fields = ['address', 'address__location']
    search_fields = ['address', 'full_name']


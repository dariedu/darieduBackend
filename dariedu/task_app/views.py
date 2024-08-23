from django.shortcuts import render
from rest_framework import viewsets

from .models import Task, Delivery
from .serializers import TaskSerializer, DeliverySerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_fields = ['is_active', 'is_completed', 'city', 'curator', 'volunteer', 'category', 'date']
    ordering_fields = ['date', 'price']


class DeliveryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows deliveries to be viewed or edited.
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    filter_fields = ['is_free', 'is_active', 'city', 'volunteer', 'route_sheet__address_route_sheet__location', 'date']
    ordering_fields = ['date']

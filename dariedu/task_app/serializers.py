from django.db.models import F  # для метода завершения задачи куратором
from rest_framework import serializers

from address_app.models import Location
from address_app.serializers import CitySerializer, CuratorSerializer
from user_app.models import User
from .models import Task, Delivery, DeliveryAssignment, TaskCategory


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    category = TaskCategorySerializer(read_only=True)
    curator = CuratorSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = [
            'id', 'category', 'name', 'volunteer_price', 'curator_price', 'description', 'start_date', 'end_date', 'volunteers_needed',
            'volunteers_taken', 'is_active', 'is_completed', 'curator', 'volunteers'
        ]


class TaskVolunteerSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    category = TaskCategorySerializer(read_only=True)

    class Meta:
        model = Task
        extends = ['volunteers']
        read_only_fields = [
            'id', 'category', 'name', 'volunteer_price', 'curator_price', 'description', 'start_date', 'end_date',
            'volunteers_needed', 'is_active', 'is_completed', 'curator', 'volunteers'
        ]


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'delivery', 'volunteer']


class LocationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'address', 'link', 'subway', 'description']


class DeliverySerializer(serializers.ModelSerializer):
    delivery_assignments = DeliveryAssignmentSerializer(many=True, source='assignments')
    curator = CuratorSerializer(read_only=True)
    location = LocationShortSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'date', 'curator', 'price', 'is_free', 'is_active', 'location',
                  'is_completed', 'in_execution', 'volunteers_needed', 'volunteers_taken', 'delivery_assignments']


class DeliveryVolunteerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Delivery
        fields = ['id', 'date', 'curator', 'price', 'is_free', 'is_active',
                  'is_completed', 'in_execution', 'volunteers_needed', 'volunteers_taken']
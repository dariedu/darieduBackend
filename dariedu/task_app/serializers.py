from django.db.models import F  # для метода завершения задачи куратором
from rest_framework import serializers

from address_app.models import Location
from address_app.serializers import CitySerializer, CuratorSerializer

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
    curator = CuratorSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'category', 'city', 'name', 'volunteer_price', 'curator_price', 'description',
            'start_date', 'end_date', 'volunteers_needed', 'is_active', 'is_completed', 'curator',
        ]
        read_only_fields = [
            'id', 'category', 'name', 'city', 'volunteer_price', 'curator_price', 'description',
            'start_date', 'end_date', 'volunteers_needed', 'is_active', 'is_completed', 'curator',
        ]


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'delivery', 'volunteer']


class LocationShortSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    class Meta:
        model = Location
        fields = ['id', 'address', 'link', 'subway', 'city', 'description']


class DeliverySerializer(serializers.ModelSerializer):
    # delivery_assignments = DeliveryAssignmentSerializer(many=True, source='assignments')
    curator = CuratorSerializer(read_only=True)
    location = LocationShortSerializer(read_only=True)
    route_sheet = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = ['id', 'date', 'curator', 'price', 'is_free', 'is_active', 'location',
                  'is_completed', 'in_execution', 'volunteers_needed', 'volunteers_taken', 'route_sheet']

    def get_route_sheet(self, obj):
        print(f"Checking route_sheet for Delivery ID: {obj.id}, in_execution: {obj.in_execution}")
        if self.context.get('is_volunteer_view', False):
            if obj.in_execution or obj.is_completed:
                return [route.id for route in obj.route_sheet.all()]
        elif self.context.get('is_curator_view', False):
            return [route.id for route in obj.route_sheet.all()]
        return []

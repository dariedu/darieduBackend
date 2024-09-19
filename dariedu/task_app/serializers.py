from django.db.models import F  # для метода завершения задачи куратором
from rest_framework import serializers
from address_app.serializers import CitySerializer
from .models import Task, Delivery, DeliveryAssignment, TaskCategory


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    category = TaskCategorySerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = [
            'id', 'category', 'name', 'price', 'description', 'start_date', 'end_date', 'volunteers_needed',
            'volunteers_taken', 'is_active', 'is_completed', 'curator', 'volunteers'
        ]

    def update(self, instance, validated_data):
        """
        Method to update task instance.
        Update logic depends on request path.

        Args:
            instance: task instance to be updated
            validated_data: data to update
        """
        view = self.context['view']
        request = self.context['request']

        # get data to update with or the old value if it was not passed
        volunteers_taken = validated_data.get('volunteers_taken', instance.volunteers_taken)

        # Вернуть по необходимости!
        # Для метода завершения задачи куратором
        is_active = validated_data.get('is_active', instance.is_active)
        is_completed = validated_data.get('is_completed', instance.is_completed)

        # update instance fields
        instance.volunteers_taken = volunteers_taken

        # Вернуть по необходимости!
        # Для метода завершения задачи куратором
        instance.is_active = is_active
        instance.is_completed = is_completed

        instance.save()

        # update relations depending on requested action
        path = request.build_absolute_uri()
        if path == view.reverse_action('task_accept', args=[instance.pk]):
            # task accept logic
            instance.volunteers.add(request.user)
        elif path == view.reverse_action('task_refuse', args=[instance.pk]):
            # task refuse logic
            instance.volunteers.remove(request.user)

        # Вернуть по необходимости!
        # Для метода завершения задачи куратором
        elif path == view.reverse_action('task_complete', args=[instance.pk]):
            # task complete logic
            instance.volunteers.update(
                volunteer_hour=F('volunteer_hour') + instance.price,
                point=F('point') + instance.price
            )

        return instance


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'delivery', 'volunteer']


class DeliverySerializer(serializers.ModelSerializer):
    delivery_assignments = DeliveryAssignmentSerializer(many=True, source='assignments')

    class Meta:
        model = Delivery
        fields = ['id', 'date', 'curator', 'price', 'is_free', 'is_active',
                  'is_completed', 'in_execution', 'volunteers_needed', 'volunteers_taken', 'delivery_assignments']

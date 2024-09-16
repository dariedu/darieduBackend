from django.contrib.auth import get_user_model  # TODO remove when authentication is ready
from django.db.models import F  # для метода завершения задачи куратором
from rest_framework import serializers
from .models import Task, Delivery, DeliveryAssignment

User = get_user_model()  # TODO remove when authentication is ready


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }

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
            # instance.volunteers.add(request.user)
            instance.volunteers.add(User.objects.get(pk=1))  # TODO swap to comment when authentication is ready
        elif path == view.reverse_action('task_refuse', args=[instance.pk]):
            # task refuse logic
            # instance.volunteers.remove(request.user)
            instance.volunteers.remove(User.objects.get(pk=1))  # TODO swap to comment when authentication is ready

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


from rest_framework import serializers

from .models import Task, Delivery


class TaskSerializer(serializers.ModelSerializer):
    # TODO we need only GET here and UPDATE to take the task
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            # TODO and all the others?
        }


class DeliverySerializer(serializers.ModelSerializer):
    # TODO we need only GET here and UPDATE to take the delivery
    class Meta:
        model = Delivery
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            # TODO and all the others?
        }

    def create(self, validated_data):
        instance = self.context['view'].get_object()
        instance.is_free = False
        instance.is_active = True
        instance.in_execution = True
        # instance.volunteer = None
        instance.volunteer = self.context['request'].user
        instance.save()
        return instance

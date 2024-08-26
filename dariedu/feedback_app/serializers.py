from rest_framework import serializers

from .models import Feedback, RequestMessage


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class RequestMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMessage
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }
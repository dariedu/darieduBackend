from attr.filters import exclude
from rest_framework import serializers

from user_app.models import User
from .models import Feedback, RequestMessage, PhotoReport


class UserShortSerializer(serializers.ModelSerializer):
    """To show curators data"""
    class Meta:
        model = User
        fields = [
            'id',
            'tg_id',
            'tg_username',
            'last_name',
            'name',
            'surname',
            'phone',
            'photo',
            'avatar',
        ]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class RequestMessageSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = RequestMessage
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class PhotoReportSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = PhotoReport
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
        }

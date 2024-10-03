from rest_framework import serializers
from .models import Feedback, RequestMessage, PhotoReport


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'type', 'text', 'user', 'delivery', 'promotion', 'created_at']

    def validate(self, data):
        feedback_type = data.get('type')
        delivery = data.get('delivery')
        promotion = data.get('promotion')

        # Валидация: отзыв может быть о доставке или поощрении, но не о двух одновременно
        if feedback_type == 'delivery' and not delivery:
            raise serializers.ValidationError("Для отзыва о доставке необходимо выбрать доставку.")
        if feedback_type == 'promotion' and not promotion:
            raise serializers.ValidationError("Для отзыва о поощрении необходимо выбрать поощрение.")
        if delivery and promotion:
            raise serializers.ValidationError(
                "Отзыв может быть связан только с одной моделью: либо доставка, либо поощрение.")

        return data


class RequestMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMessage
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class PhotoReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoReport
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
        }

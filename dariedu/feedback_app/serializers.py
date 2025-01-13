from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Feedback, RequestMessage, PhotoReport


User = get_user_model()


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
            'photo_view',
        ]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'type', 'text', 'user', 'delivery', 'task', 'promotion', 'created_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
        }

    def validate(self, data):
        feedback_type = data.get('type')
        delivery = data.get('delivery')
        promotion = data.get('promotion')
        task = data.get('task')

        # Валидация: отзыв может быть о доставке или поощрении, но не о двух одновременно
        if feedback_type in 'сompleted_delivery' and not delivery:
            raise serializers.ValidationError("Для отзыва о доставке необходимо выбрать доставку.")
        if feedback_type == 'promotion' and not promotion:
            raise serializers.ValidationError("Для отзыва о поощрении необходимо выбрать поощрение.")
        if feedback_type == 'task' and not task:
            raise serializers.ValidationError("Для отзыва о добром дело необходимо выбрать доброе дело.")
        if delivery and promotion:
            raise serializers.ValidationError(
                "Отзыв может быть связан только с одной моделью: либо доставка, либо поощрение.")

        return data


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
    photo = serializers.ImageField(write_only=True)

    class Meta:
        model = PhotoReport
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'photo_view': {'read_only': True},
            'photo_download': {'read_only': True},
        }

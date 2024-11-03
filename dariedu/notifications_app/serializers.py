from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse
from rest_framework import serializers

from .models import Notification
from promo_app.models import Promotion
from task_app.models import Task


class NotificationSerializer(serializers.ModelSerializer):
    promotion_id = serializers.IntegerField(required=False)
    task_id = serializers.IntegerField(required=False)
    action_type = serializers.ChoiceField(choices=['confirm', 'cancel'], required=True)

    class Meta:
        model = Notification
        fields = ['promotion_id', 'task_id', 'title', 'action_type']

    def create(self, validated_data):
        promotion_id = validated_data.pop('promotion_id', None)
        task_id = validated_data.pop('task_id', None)
        title = validated_data.get('title')
        action_type = validated_data.get('action_type')

        if promotion_id is not None:
            promotion = get_object_or_404(Promotion, id=promotion_id)
            data_str = promotion.start_date.strftime('%d.%m.%Y')
            time_str = promotion.start_date.strftime('%H:%M')

            url = reverse('admin:promo_app_promotion_change', args=[promotion.id])
            if action_type == 'confirm':
                message_text = (f'Пользователь {promotion.users.first().tg_username},'
                                f' подтвердил запись поощрения: "{promotion.name}", '
                                f'{data_str} в {time_str}!')
            else:
                message_text = (f'Пользователь {promotion.users.first().tg_username},'
                                f' отменил запись поощрения: "{promotion.name}", '
                                f'{data_str} в {time_str}!')
        elif task_id is not None:
            task = get_object_or_404(Task, id=task_id)
            data_str = task.start_date.strftime('%d.%m.%Y')
            time_str = task.start_date.strftime('%H:%M')

            url = reverse('admin:task_app_task_change', args=[task.id])
            if action_type == 'confirm':
                message_text = (f'Пользователь {task.volunteers.first().tg_username},'
                                f' подтвердил запись на Доброе дело: "{task.name}", '
                                f'{data_str} в {time_str}!')
            else:
                message_text = (f'Пользователь {task.volunteers.first().tg_username},'
                                f' отменил запись на Доброе дело: "{task.name}", '
                                f'{data_str} в {time_str}!')

        else:
            raise serializers.ValidationError("Either promotion_id or task_id must be provided.")

        notification = Notification.objects.create(
            title=title,
            text=message_text,
            obj_link=url,
            created=timezone.now()
        )
        return notification

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse
from rest_framework import serializers
from .models import Notification
from promo_app.models import Promotion


class NotificationSerializer(serializers.ModelSerializer):
    promotion_id = serializers.IntegerField()

    class Meta:
        model = Notification
        fields = ['title', 'text', 'promotion_id']

    def create(self, validated_data):
        promotion_id = validated_data.get('promotion_id')
        title = validated_data.get('title')
        promotion = get_object_or_404(Promotion, id=promotion_id)

        url = reverse('admin:promo_app_promotion_change', args=[promotion.id])
        # url = f'http://127.0.0.1:8000/admin/promo_app/promotion/{promotion.id}/change/'
        message_text = (f'Пользователь {promotion.users.first().tg_username},'
                        f' отменил использование поощрения: "{promotion.name}", '
                        f'{promotion.start_date.strftime("%d.%m.%Y %H:%M")}!')
        notification = Notification.objects.create(
            title=title,
            text=message_text,
            form=url,
            created=timezone.now()
        )
        return notification

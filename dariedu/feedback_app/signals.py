from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import RequestMessage
from notifications_app.models import Notification


@receiver(post_save, sender=RequestMessage)
def create_feedback(sender, instance, created, **kwargs):
    if created:
        notification = Notification.objects.create(
            title=instance.type,
            text=f'Пользователь {instance.user.tg_username} оставил заявку "{instance.text}"',
            form=instance.form,
            created=timezone.now()
        )
        notification.save()

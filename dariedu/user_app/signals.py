from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from notifications_app.models import Notification
from user_app.models import User


@receiver(post_save, sender=User)
def create_feedback(sender, instance, created, **kwargs):
    if created:
        notification = Notification.objects.create(
            title='Новый пользователь',
            text=f'Зарегистрировался новый пользователь {instance}',
            # form=instance.form,
            created=timezone.now()
        )
        notification.save()

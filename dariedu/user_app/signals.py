from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from notifications_app.models import Notification
from user_app.models import User


@receiver(post_save, sender=User)
def create_user(sender, instance, created, **kwargs):
    if created:
        notification = Notification.objects.create(
            title='Новый пользователь',
            text=f'Зарегистрировался новый пользователь {instance}',
            obj_link=instance.get_absolute_url(),
            created=timezone.now()
        )
        notification.save()
    else:
        instance.update_rating()


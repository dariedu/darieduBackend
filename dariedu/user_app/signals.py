from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.utils import timezone

from notifications_app.models import Notification
from user_app.tasks import export_to_google, update_google_sheet


User = get_user_model()


@receiver(post_save, sender=User)
def create_user(sender, instance, created, **kwargs):
    if created:
        if instance.is_adult:
            notification = Notification.objects.create(
                title='Новый пользователь',
                text=f'Зарегистрировался новый пользователь {instance}',
                obj_link=instance.get_absolute_url(),
                created=timezone.now()
            )
        else:
            notification = Notification.objects.create(
                title='Несовершеннолетний пользователь',
                text=f'Зарегистрировался несовершеннолетний пользователь {instance}',
                obj_link=instance.get_absolute_url(),
                created=timezone.now()
            )
        notification.save()
    else:
        instance.update_rating()


@receiver(post_save, sender=User)
def create_users(sender, instance, created, **kwargs):
    if created:
        user_id = instance.id
        export_to_google.apply_async(args=[user_id], countdown=10)
    else:
        user_id = instance.id
        update_google_sheet.apply_async(args=[user_id], countdown=15)

from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.utils import timezone
import logging

from notifications_app.models import Notification
from user_app.tasks import export_to_google, update_google_sheet, send_message_to_telegram_is_admin
# from statistics_app.models import Statistics

User = get_user_model()
logger = logging.getLogger('django.server')


@receiver(post_save, sender=User)
def create_user(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        age = today.year - instance.birthday.year

        if (today.month, today.day) < (instance.birthday.month, instance.birthday.day):
            age -= 1
        instance.is_adult = age >= 18
        instance.save()

        if instance.is_adult:
            try:
                name = instance.tg_username if instance.tg_username else f'{instance.name} {instance.last_name}'
                message = f'Зарегистрировался новый пользователь {name}'
                send_message_to_telegram_is_admin.apply_async(args=[message], countdown=10)
            except Exception as e:
                logger.error(f"An error occurred while processing the volunteer signup: {e}")

            notification = Notification.objects.create(
                title='Новый пользователь',
                text=f'Зарегистрировался новый пользователь {instance}',
                obj_link=instance.get_absolute_url(),
                created=timezone.now()
            )
            notification.save()
        else:
            try:
                name = instance.tg_username if instance.tg_username else f'{instance.name} {instance.last_name}'
                message = f'Зарегистрировался несовершеннолетний пользователь {name}'
                send_message_to_telegram_is_admin.apply_async(args=[message], countdown=10)
            except Exception as e:
                logger.error(f"An error occurred while processing the volunteer signup: {e}")

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


# @receiver(post_save, sender=User)
# def update_volunteer_stats(sender, instance, created, **kwargs):
#     today = timezone.now().date()
#
#     if created:
#         Statistics.objects.create(
#             volunteer=instance,
#             points=instance.point,
#             volunteer_hours=instance.volunteer_hour,
#             period=today
#         )
#     else:
#         stats, _ = Statistics.objects.get_or_create(
#             volunteer=instance,
#             period=today
#         )
#
#         if instance.old_point > instance.point:
#             point_difference = instance.old_point - instance.point
#             stats.points += point_difference
#
#         volunteer_hour_difference = instance.volunteer_hour - instance.old_volunteer_hour
#         if volunteer_hour_difference > 0:
#             stats.volunteer_hours += volunteer_hour_difference
#         else:
#             stats.volunteer_hours = max(0, stats.volunteer_hours + volunteer_hour_difference)
#
#         stats.save()

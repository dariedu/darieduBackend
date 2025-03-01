from datetime import timedelta
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .models import Promotion, Participation
from notifications_app.models import Notification
from .tasks import send_message_to_telegrams


@receiver(post_save, sender=Promotion)
def signal_for_promo_tickets(sender, instance, created, **kwargs):
    if created:
        time = instance.start_date - timedelta(hours=1)
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=time.minute,
            hour=time.hour,
            day_of_month=time.day,
            month_of_year=time.month,
            timezone=timezone.get_current_timezone()
        )
        PeriodicTask.objects.create(
            crontab=schedule,
            name=f'Event - {instance.name}',
            task='promo_app.tasks.event_start_promotion',
            args=[instance.pk]
        )


@receiver(post_save, sender=Participation)
def signal_for_promo_users(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        name = instance.promotion.name
        notification = Notification.objects.create(
            title='Запись на Поощрение',
            text=f'Волонтер {user.tg_username} записался на поощрение '
                 f'"{name}"!',
            obj_link=instance.promotion.get_absolute_url(),
        )
        notification.save()

        send_message_to_telegrams.apply_async(args=[instance.promotion.id, user.id], countdown=10)

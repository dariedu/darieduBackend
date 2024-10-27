from datetime import timedelta

from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .models import Promotion


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

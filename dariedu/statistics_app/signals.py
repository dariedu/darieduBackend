import logging
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import VolunteerStats

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(pre_save, sender=User)
def update_volunteer_stats(sender, instance, **kwargs):
    # Проверка изменений полей
    if instance.pk is not None and (
            instance.tracker.has_changed('volunteer_hour') or instance.tracker.has_changed('point')):
        logger.debug(f"Сигнал update_volunteer_stats вызван для пользователя ID {instance.pk}. "
                     f"Изменение часов: {instance.tracker.previous('volunteer_hour')} -> {instance.volunteer_hour}, "
                     f"Изменение баллов: {instance.tracker.previous('point')} -> {instance.point}")

        # Создаем новую запись в VolunteerStats с обновленными значениями
        VolunteerStats.objects.create(
            volunteer=instance,
            volunteer_hours=instance.volunteer_hour,
            points=instance.point
        )

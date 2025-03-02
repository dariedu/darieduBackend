from django.db.models.signals import m2m_changed
from django.dispatch import receiver

import logging
from django.contrib.auth import get_user_model

from .export_delivery import export_deliveries
from .models import DeliveryAssignment, Task, Delivery
from .tasks import send_message_to_telegram, send_massage_to_telegram_delivery
from notifications_app.models import Notification
from .export_gs_tasks import export_to_google_tasks, cancel_task_in_google_tasks, export_to_google_delivery, \
    cancel_task_in_google_delivery


User = get_user_model()

logger = logging.getLogger('django.server')


@receiver(m2m_changed, sender=DeliveryAssignment.volunteer.through)
def update_delivery_status(sender, instance, action, **kwargs):
    if action == 'post_add':
        delivery = instance.delivery
        volunteers_needed = delivery.volunteers_needed
        volunteers_taken = delivery.volunteers_taken + 1
        delivery.volunteers_taken = volunteers_taken
        if volunteers_taken == volunteers_needed:
            # delivery.in_execution = True
            delivery.is_free = False
        delivery.save()
    if action == 'post_remove':
        delivery = instance.delivery
        volunteers_taken = delivery.volunteers_taken - 1
        delivery.volunteers_taken = volunteers_taken
        if volunteers_taken < delivery.volunteers_needed:
            # delivery.in_execution = False
            delivery.is_free = True
        delivery.save()


@receiver(m2m_changed, sender=Task.volunteers.through)
def send_message_to_telegram_on_volunteer_signup(sender, instance, action, **kwargs):
    if action == 'post_add':

        volunteer_ids = kwargs.get('pk_set', [])
        for volunteer_id in volunteer_ids:

            try:
                user = User.objects.get(id=volunteer_id)
            except User.DoesNotExist:
                logger.error(f"User  with id {volunteer_id} does not exist.")
                return

            message = (f'Волонтер {user.tg_username if user.tg_username else user.name}'
                       f' записался на выполнение Доброго дела "{instance.name}"!')

            send_message_to_telegram.apply_async(args=[instance.id, message], countdown=15)

            volunteer = instance.volunteers.get(id=volunteer_id)

            notification = Notification.objects.create(
                title='Запись на выполнение Доброго дела',
                text=f'Волонтер {volunteer.tg_username if volunteer.tg_username else volunteer.name} '
                     f'записался на выполнение Доброго дела "{instance.name}"!',
                obj_link=instance.get_absolute_url(),
            )
            notification.save()

    if action == 'post_remove':
        removed_volunteers = kwargs.get('pk_set', set())

        for user_id in removed_volunteers:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"User  with id {user_id} does not exist.")
                return

            message = (f'Волонтер {user.tg_username if user.tg_username else user.name} '
                       f'отказался от выполнения Доброго дела "{instance.name}"!')
            send_message_to_telegram.apply_async(args=[instance.id, message], countdown=15)

            notification = Notification.objects.create(
                title='Отказ от выполнения Доброго дела',
                text=f'Волонтер {user.tg_username if user.tg_username else user.name} '
                     f'отказался от выполнения Доброго дела "{instance.name}"!',
                obj_link=instance.get_absolute_url(),
            )
            notification.save()


@receiver(m2m_changed, sender=DeliveryAssignment.volunteer.through)
def send_message_to_telegram_on_volunteer_signup_delivery(sender, instance, action, **kwargs):
    if action == 'post_add':
        volunteer_ids = kwargs.get('pk_set', [])

        for volunteer_id in volunteer_ids:

            try:
                user = User.objects.get(id=volunteer_id)
            except User.DoesNotExist:
                logger.error(f'User  with id {volunteer_id} does not exist.')
                continue

            date = instance.delivery.date.strftime('%d.%m.%Y')
            location = instance.delivery.location.address
            message = (f'Волонтер {user.tg_username if user.tg_username else user.name} '
                       f'записался на доставку дата: {date}, локация: {location}!')
            send_massage_to_telegram_delivery.apply_async(args=[instance.delivery.id, message], countdown=15)

    if action == 'post_remove':
        removed_volunteers = kwargs.get('pk_set', set())

        for user_id in removed_volunteers:

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f'User  with id {user_id} does not exist.')
                continue

            date = instance.delivery.date.strftime('%d.%m.%Y')
            location = instance.delivery.location.address
            message = (f'Волонтер {user.tg_username if user.tg_username else user.name} '
                       f'отказался от доставки дата: {date}, локация: {location}!')
            send_massage_to_telegram_delivery.apply_async(args=[instance.delivery.id, message], countdown=15)


@receiver(m2m_changed, sender=Task.volunteers.through)
def create_task(sender, instance, action, **kwargs):
    if action == 'post_add':
        # Проверяем, есть ли волонтеры
        if instance.volunteers.exists():
            task_id = instance.id
            user_id = instance.volunteers.first().id
            export_to_google_tasks.apply_async(args=[user_id, task_id], countdown=30)
    if action == 'post_remove':
        removed_volunteers = kwargs.get('pk_set', set())
        for user_id in removed_volunteers:
            task_id = instance.id
            cancel_task_in_google_tasks.apply_async(args=[user_id, task_id], countdown=30)

@receiver(m2m_changed, sender=DeliveryAssignment.volunteer.through)
def create_delivery_assignment(sender, instance, action, **kwargs):
    if action == 'post_add':
        delivery_id = instance.delivery.id
        user_id = instance.volunteer.first().id
        export_to_google_delivery.apply_async(args=[user_id, delivery_id], countdown=30)
    if action == 'post_remove':
        removed_volunteers = kwargs.get('pk_set', set())
        for user_id in removed_volunteers:
            delivery_id = instance.delivery.id
            cancel_task_in_google_delivery.apply_async(args=[user_id, delivery_id], countdown=30)


@receiver(post_save, sender=Delivery)
def export_delivery_to_gs(sender, instance, created, **kwargs):
    """
    Функция для экспорта данных о доставке в Google Sheets
    """
    try:
        if instance.is_completed:
            delivery_id = instance.id
            export_deliveries.apply_async(args=[delivery_id], countdown=30)
    except Exception as e:
        logger.error(f'Error exporting delivery to Google Sheets: {e}')

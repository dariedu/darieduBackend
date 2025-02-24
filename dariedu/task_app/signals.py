from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
import logging

from .models import DeliveryAssignment, Task, Delivery
from .tasks import send_message_to_telegram
from notifications_app.models import Notification
from .export_gs_tasks import export_to_google_tasks, cancel_task_in_google_tasks, export_to_google_delivery, \
    cancel_task_in_google_delivery


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


@receiver(post_save, sender=Delivery)
def update_points_hours(sender, instance, created, **kwargs):
    try:
        if instance.is_completed:
            curator = instance.curator
            curator.update_volunteer_hours(hours=curator.volunteer_hour + 4,
                                           point=curator.point + 4)
            curator.save(update_fields=['volunteer_hour', 'point'])

            assignments = DeliveryAssignment.objects.filter(delivery=instance)
            for assignment in assignments:
                for volunteer in assignment.volunteer.all():
                    volunteer.update_volunteer_hours(
                        hours=volunteer.volunteer_hour + instance.price,
                        point=volunteer.point + instance.price
                    )
                    volunteer.save(update_fields=['volunteer_hour', 'point'])
    except Exception as e:
        logger.error(f'Error updating points and hours: {e}')


@receiver(post_save, sender=Task)
def update_points_hours_task(sender, instance, created, **kwargs):
    try:
        if instance.is_completed:
            curator = instance.curator
            curator.update_volunteer_hours(hours=curator.volunteer_hour + instance.volunteer_price,
                                           point=curator.point + instance.volunteer_price)
            curator.save(update_fields=['volunteer_hour', 'point'])

            for volunteer in instance.volunteers.all():
                volunteer.update_volunteer_hours(
                    hours=volunteer.volunteer_hour + instance.volunteer_price,
                    point=volunteer.point + instance.volunteer_price
                )
                volunteer.save(update_fields=['volunteer_hour', 'point'])
    except Exception as e:
        logger.error(f'Error updating points and hours: {e}')


@receiver(m2m_changed, sender=Task.volunteers.through)
def send_message_to_telegram_on_volunteer_signup(sender, instance, action, **kwargs):
    if action == 'post_add':
        task_id = instance.id
        send_message_to_telegram.delay(task_id)
        user = instance.volunteers.first()
        notification = Notification.objects.create(
            title='Запись на выполнение Доброго дела',
            text=f'Волонтер {user.tg_username} записался на выполнение Доброго дела '
                 f'"{instance.name}"!',
            obj_link=instance.get_absolute_url(),
        )
        notification.save()

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

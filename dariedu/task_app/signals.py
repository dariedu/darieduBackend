from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import DeliveryAssignment, Task
from .tasks import send_message_to_telegram
from notifications_app.models import Notification
from .export_gs_tasks import export_to_google_tasks, cancel_task_in_google_tasks, export_to_google_delivery, \
    cancel_task_in_google_delivery


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
            export_to_google_tasks.apply_async(args=[user_id, task_id], countdown=60)
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
        export_to_google_delivery.delay(user_id, delivery_id)
    if action == 'post_remove':
        removed_volunteers = kwargs.get('pk_set', set())
        for user_id in removed_volunteers:
            delivery_id = instance.delivery.id
            cancel_task_in_google_delivery.apply_async(args=[user_id, delivery_id], countdown=30)

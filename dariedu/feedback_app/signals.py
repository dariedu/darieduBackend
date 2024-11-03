from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import RequestMessage
from notifications_app.models import Notification
from django.conf import settings
from django.core.mail import send_mail
from .models import Feedback


@receiver(post_save, sender=RequestMessage)
def create_feedback(sender, instance, created, **kwargs):
    if created:
        notification = Notification.objects.create(
            title=instance.type,
            text=f'Пользователь {instance.user.tg_username} оставил заявку "{instance.about_location}"',
            obj_link=instance.get_absolute_url(),
            created=timezone.now()
        )
        notification.save()


@receiver(post_save, sender=Feedback)
def send_suggestion_email(sender, instance, created, **kwargs):
    if created and instance.type == 'suggestion':
        notification = Notification.objects.create(
            title="Вопросы и предложения",
            text=f"Новые вопросы и предложения от пользователя {instance.user}",
            obj_link=instance.get_absolute_url(),
            created=timezone.now()
        )
        notification.save()
        subject = f"Новые вопросы и предложения от пользователя {instance.user}"
        message = (
            f"Текст: {instance.text}\n"
            f"Дата создания: {instance.created_at}\n"
            f"Пользователь: {instance.user.name}"
        )

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )

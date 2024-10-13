# import datetime
from datetime import timedelta, datetime
import json
from pprint import pprint
import requests
from celery import shared_task
from django.conf import settings
from celery.utils.log import get_task_logger
from django.db.models import F
from django.utils import timezone

from .keyboard import keyboard_task, keyboard_delivery
from .models import Task, Delivery

logger = get_task_logger(__name__)
url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'


@shared_task
def send_message_to_telegram(task_id):
    """
    Notification to the supervisor about a volunteer taking on a task.
    """
    task = Task.objects.get(id=task_id)
    curator = task.curator
    chat_id = curator.tg_id
    volunteers = task.volunteers
    name = volunteers.first().name
    message = f"Пользователь {name} записался на выполнение задачи {task.name}!"
    payload = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, json=payload)
    return response.json()


@shared_task
def send_task_to_telegram(task_id):
    """
    Notification of confirmation of participation in task.
    """
    task = Task.objects.get(id=task_id)
    chat_id = task.curator.tg_id
    volunteer_tg_ids = [tg_id for tg_id in task.volunteers.values_list('tg_id', flat=True)]
    timedate = task.end_date
    timedate = timedate.strftime('%d.%m.%Y %H:%M')
    data = {
        'task_id': task_id,
        'curator_tg_id': chat_id
    }
    messages = f'Подтвердите участие в задаче {task.name}, срок выполнения {timedate}!'
    keyboard = keyboard_task(data)
    reply_markup = json.dumps(keyboard)
    for volunteer_tg_id in volunteer_tg_ids:
        payload = {
            'chat_id': volunteer_tg_id,
            'text': messages,
            'reply_markup': reply_markup
        }
        response = requests.post(url, json=payload)
        pprint(response.json())

@shared_task
def check_tasks():
    today = timezone.make_aware(datetime.today())
    tasks = Task.objects.filter(start_date__date=today)
    for task in tasks:
        if task.end_date.date() == today.date():
            if task.end_date >= timezone.now():
                eta = task.end_date - timedelta(hours=3)
            else:
                eta = timezone.now()
        else:
            eta = task.start_date + (task.end_date - task.start_date) // 2
        if eta >= timezone.now():
            send_task_to_telegram.apply_async(args=[task.id], eta=eta)


@shared_task
def send_delivery_to_telegram(delivery_id):
    """
    Notification of confirmation of participation in delivery.
    """
    delivery = Delivery.objects.get(id=delivery_id)
    volunteer_tg_ids = [volunteer.tg_id for assignment in delivery.assignments.all() for volunteer in
                        assignment.volunteer.all()]

    if not volunteer_tg_ids:
        return

    timedate = delivery.date
    timedate = timedate.strftime('%d.%m.%Y %H:%M')
    curator_tg_id = delivery.curator.tg_id
    data = {
        'delivery_id': delivery_id,
        'curator_tg_id': curator_tg_id
    }

    keyboard = keyboard_delivery(data)
    messages = f'Подтвердите участие в доставке, в {timedate}!'
    reply_markup = json.dumps(keyboard)

    for volunteer_tg_id in volunteer_tg_ids:
        payload = {
            'chat_id': volunteer_tg_id,
            'text': messages,
            'reply_markup': reply_markup
        }
        response = requests.post(url, json=payload)
        pprint(response.json())


@shared_task
def check_deliveries():
    deliveries = Delivery.objects.filter(date__gte=timezone.now())
    for delivery in deliveries:
        eta = delivery.date - timedelta(hours=3)
        if timezone.now() <= eta:
            send_delivery_to_telegram.apply_async(args=[delivery.id], eta=eta)


@shared_task
def complete_task():
    tasks = Task.objects.filter(end_date__gte=timezone.now() - timedelta(hours=1))
    for task in tasks:
        if task.is_completed:
            task.is_active = False
            task.save()
        else:
            task.is_active = False
            task.is_completed = True
            task.volunteers.update(volunteer_hours=F('volunteer_hours') + task.volunteer_price)
            task.curator.volunteer_hours += task.curator_price
            task.save()


@shared_task
def complete_delivery():
    deliveries = Delivery.objects.filter(date__gte=timezone.now() - timedelta(hours=3))
    for delivery in deliveries:
        if delivery.is_completed:
            delivery.is_active = False
            delivery.is_free = False
            delivery.in_execution = False
            delivery.is_active = False
            delivery.save()
        else:
            delivery.is_active = False
            delivery.is_completed = True
            delivery.in_execution = False
            delivery.is_free = False
            delivery.volunteers.update(volunteer_hours=F('volunteer_hours') + delivery.price)
            delivery.curator.volunteer_hours += 4
            delivery.save()

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
            if task.start_date >= timezone.now():
                eta = task.start_date - timedelta(hours=3)
            else:
                eta = timezone.now()
            if eta < timezone.now().replace(hour=9, minute=0, second=0, microsecond=0):
                eta = timezone.now().replace(hour=9, minute=5, second=0, microsecond=0)
        else:
            date = task.start_date__date + (task.end_date__date - task.start_date__date) // 2
            eta = timezone.make_aware(datetime.combine(date, datetime.time(10)))
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
    deliveries = Delivery.objects.filter(date__date=timezone.make_aware(datetime.today()), date__gte=timezone.now())
    for delivery in deliveries:
        eta = delivery.date - timedelta(hours=3)
        if eta <= timezone.now().replace(hour=9, minute=0, second=0, microsecond=0):
            eta = timezone.now().replace(hour=9, minute=5, second=0, microsecond=0)
        if timezone.now() <= eta:
            send_delivery_to_telegram.apply_async(args=[delivery.id], eta=eta)


@shared_task
def complete_task(task_id):
    task = Task.objects.get(id=task_id)
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
def check_complete_task():
    tasks = Task.objects.filter(end_date__date=timezone.make_aware(datetime.today()))
    for task in tasks:
        eta = task.end_date + timedelta(hours=1)
        complete_task.apply_async(args=[task.id], eta=eta)


@shared_task
def complete_delivery(delivery_id):
    delivery = Delivery.objects.get(id=delivery_id)
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


@shared_task
def check_complete_delivery():
    deliveries = Delivery.objects.filter(date__date=timezone.make_aware(datetime.today()))
    for delivery in deliveries:
        eta = delivery.date + timedelta(hours=3)
        complete_delivery.apply_async(args=[delivery.id], eta=eta)


@shared_task
def activate_delivery(delivery_id):
    delivery = Delivery.objects.get(id=delivery_id)
    if delivery.is_active:
        delivery.in_execution = True
        delivery.save()


@shared_task
def check_activate_delivery():
    deliveries = Delivery.objects.filter(date__date=timezone.make_aware(datetime.today()))
    for delivery in deliveries:
        eta = delivery.date - timedelta(hours=0, minutes=30)
        activate_delivery.apply_async(args=[delivery.id], eta=eta)


@shared_task
def duplicate_tasks_for_next_week():
    # Текущая дата для фильтрации задач на этой неделе
    today = timezone.now().date()
    end_of_week = today + timedelta(days=(6 - today.weekday()))

    # Задачи текущей недели
    tasks_to_duplicate = Task.objects.filter(
        start_date__range=(today, end_of_week),
        is_active=True,
        is_completed=False
    )

    # Копии задач на следующую неделю
    for task in tasks_to_duplicate:
        task.pk = None  # сброс первичного ключа для создания новой записи
        task.start_date += timedelta(weeks=1)  # обновление даты на следующую неделю
        task.end_date += timedelta(weeks=1)
        task.is_active = False  # неактивные по умолчанию
        task.volunteers.clear()  # удаление волонтёров
        task.save()

import json
import zoneinfo

import requests

from datetime import timedelta, datetime

from pprint import pprint

from celery import shared_task
from django.conf import settings
from celery.utils.log import get_task_logger
from django.db.models import F
from django.utils import timezone

from .keyboard import keyboard_task, keyboard_delivery
from .models import Task, Delivery

ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)

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
    name = volunteers.first().tg_username
    message = f'Волонтер {name} записался на выполнение Доброго дела "{task.name}"!'
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
    timedate = timedate.astimezone(ZONE).strftime('%d.%m.%Y')
    data = {
        'task_id': task_id,
        'curator_tg_id': chat_id
    }
    messages = f'Подтвердите выполнение Доброго дела "{task.name}", срок выполнения {timedate}!'
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
            if task.start_date >= timezone.make_aware(datetime.today()):
                eta = task.start_date - timedelta(hours=3)
            else:
                eta = timezone.make_aware(datetime.today())
        else:
            date = task.start_date.date + (task.end_date.date - task.start_date.date) // 2
            eta = timezone.make_aware(datetime.combine(date, datetime.time(task.start_date.time)))
        if eta >= timezone.make_aware(datetime.today()):
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
    date_str = timedate.astimezone(ZONE).strftime('%d.%m.%Y')
    time_str = timedate.astimezone(ZONE).strftime('%H:%M')
    curator_tg_id = delivery.curator.tg_id
    data = {
        'delivery_id': delivery_id,
        'curator_tg_id': curator_tg_id
    }

    keyboard = keyboard_delivery(data)
    messages = f'Подтвердите участие в Благотворительной доставке {date_str} в {time_str}!'
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
    deliveries = Delivery.objects.filter(date__date=timezone.make_aware(datetime.today()),
                                         date__gte=timezone.make_aware(datetime.today()))
    for delivery in deliveries:
        eta = delivery.date - timedelta(hours=3)
        if timezone.make_aware(datetime.today()) <= eta:
            send_delivery_to_telegram.apply_async(args=[delivery.id], eta=eta)


@shared_task
def complete_task(task_id):
    task = Task.objects.get(id=task_id)
    if task.is_completed:
        task.is_active = False
        task.save(update_fields=['is_active'])
    else:
        task.is_active = False
        task.is_completed = True
        for volunteer in task.volunteers.all():
            volunteer.update_volunteer_hours(
                hours=volunteer.volunteer_hour + task.volunteer_price,
                point=volunteer.point + task.volunteer_price
            )
            volunteer.save(update_fields=['volunteer_hour', 'point'])

        curator = task.curator
        curator.update_volunteer_hours(
            hours=curator.volunteer_hour + task.curator_price,
            point=curator.point + task.curator_price
        )
        curator.save(update_fields=['volunteer_hour', 'point'])
        task.save(update_fields=['is_completed', 'is_active'])


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
        delivery.save(update_fields=['is_active', 'is_free', 'in_execution'])
    else:
        delivery.is_active = False
        delivery.is_completed = True
        delivery.in_execution = False
        delivery.is_free = False
        curator = delivery.curator
        curator.update_volunteer_hours(hours=curator.volunteer_hour + 4,
                                       point=curator.point + 4)
        curator.save(update_fields=['volunteer_hour', 'point'])
        for assignment in delivery.assignments.all():
            for volunteer in assignment.volunteer.all():
                volunteer.update_volunteer_hours(
                    hours=volunteer.volunteer_hour + delivery.price,
                    point=volunteer.point + delivery.price
                )
                volunteer.save(update_fields=['volunteer_hour', 'point'])
        delivery.save(update_fields=['is_completed', 'is_active', 'in_execution', 'is_free'])


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
        delivery.save(update_fields=['in_execution'])


@shared_task
def check_activate_delivery():
    deliveries = Delivery.objects.filter(date__date=timezone.make_aware(datetime.today()))
    for delivery in deliveries:
        eta = delivery.date - timedelta(hours=1, minutes=0)
        activate_delivery.apply_async(args=[delivery.id], eta=eta)


@shared_task
def duplicate_delivery_for_next_week():
    today = timezone.make_aware(datetime.today()).date()
    end_of_week = today + timedelta(days=(6 - today.weekday()))

    deliveries_to_duplicate = Task.objects.filter(
        date__range=(today, end_of_week),
    )

    for delivery in deliveries_to_duplicate:
        new_delivery = Delivery.objects.create(
            curator=delivery.curator,
            location=delivery.location,
            price=delivery.price,
            date=delivery.date + timedelta(weeks=1),
            is_active=False,
            is_completed=False,
            in_execution=False,
            is_free=True,
            volunteers_needed=delivery.volunteers_needed,
            volunteers_taken=0,
        )
        new_delivery.route_sheet.add(*delivery.route_sheet.all())
        new_delivery.save()

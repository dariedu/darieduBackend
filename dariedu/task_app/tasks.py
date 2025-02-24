import json
import zoneinfo
import requests
from datetime import timedelta, datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from django.conf import settings
from .keyboard import keyboard_task, keyboard_delivery
from .models import Task, Delivery


ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)

logger = get_task_logger('celery_log')

url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'


@shared_task
def send_message_to_telegram(task_id):
    """
    Notification to the supervisor about a volunteer taking on a task.
    """
    logger.info(f'Starting send_message_to_telegram for task_id: {task_id}')
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f"Task with id {task_id} does not exist.")
        return

    curator = task.curator
    chat_id = curator.tg_id
    volunteers = task.volunteers
    name = volunteers.first().tg_username
    message = f'Волонтер {name} записался на выполнение Доброго дела "{task.name}"!'
    payload = {'chat_id': chat_id, 'text': message}

    try:
        response = requests.post(url, json=payload)
        logger.info(f'Message sent to Telegram chat_id {chat_id}: {message}')
        return response.json()
    except Exception as e:
        logger.error(f'Error sending message to Telegram: {e}')


@shared_task
def send_task_to_telegram(task_id):
    """
    Notification of confirmation of participation in task.
    """
    logger.info(f'Starting send_task_to_telegram for task_id: {task_id}')
    try:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            logger.error(f"Task with id {task_id} does not exist.")
            return

        chat_id = task.curator.tg_id
        volunteer_tg_ids = [tg_id for tg_id in task.volunteers.values_list('tg_id', flat=True)]
        timedate = task.end_date
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
            try:
                requests.post(url, json=payload)
                logger.info(f'Message sent to volunteer {volunteer_tg_id}: {messages}')
            except Exception as e:
                logger.error(f'Error sending message to volunteer {volunteer_tg_id}: {e}')

    except Exception as e:
        logger.error(f'Error sending task to Telegram: {e}')


@shared_task
def check_tasks():
    logger.info('Checking tasks')
    try:
        today = timezone.make_aware(datetime.today())
        logger.info(f'Checking tasks for date: {today.date()}')

        tasks = Task.objects.filter(start_date__date=today)
        for task in tasks:
            logger.info(f'Processing task: {task.id} - {task.name}')

            if task.end_date.date() == today.date():
                eta = task.start_date - timedelta(hours=3)
                logger.info(f'Setting ETA for task {task.id} to {eta}')
            else:
                date = task.start_date.date() + (task.end_date.date() - task.start_date.date()) // 2
                eta = timezone.make_aware(datetime.combine(date, datetime.time(task.start_date.time)))
                logger.info(f'Setting ETA for task {task.id} to {eta}')

            send_task_to_telegram.revoke(task.id, terminate=True)
            logger.info(f'Revoked previous task for task_id: {task.id}')
            send_task_to_telegram.apply_async(args=[task.id], eta=eta)
            logger.info(f'Scheduled send_task_to_telegram for task_id: {task.id} with ETA: {eta}')

    except Exception as e:
        logger.error(f'Error checking tasks: {e}')


@shared_task
def send_delivery_to_telegram(delivery_id):
    """
    Notification of confirmation of participation in delivery.
    """
    logger.info(f'Starting send_delivery_to_telegram for delivery_id: {delivery_id}')

    try:
        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            logger.error(f'Delivery with id {delivery_id} does not exist.')
            return

        volunteer_tg_ids = [volunteer.tg_id for assignment in delivery.assignments.all() for volunteer in
                            assignment.volunteer.all()]

        if not volunteer_tg_ids:
            logger.warning(f'No volunteers found for delivery_id: {delivery_id}')
            return

        timedate = delivery.date
        date_str = timedate.strftime('%d.%m.%Y')
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
            try:
                requests.post(url, json=payload)
                logger.info(f'Message sent to volunteer {volunteer_tg_id}: {messages}')
            except Exception as e:
                logger.error(f'Error sending message to volunteer {volunteer_tg_id}: {e}')

    except Exception as e:
        logger.error(f'Error sending delivery to Telegram: {e}')


def check_deliveries():
    logger.info(f'Checking deliveries for date: {datetime.today()}')
    try:
        try:
            deliveries = Delivery.objects.filter(date__date=timezone.make_aware(datetime.today()))
            logger.info(f'Found {len(deliveries)} deliveries for today.')
        except Exception as e:
            logger.error(f'Error fetching deliveries: {e}')
            return

        for delivery in deliveries:
            eta = delivery.date - timedelta(hours=3)
            logger.info(f'Revoking previous task for delivery_id: {delivery.id}')
            send_delivery_to_telegram.revoke(delivery.id, terminate=True)
            logger.info(f'Scheduling send_delivery_to_telegram for delivery_id: {delivery.id} with ETA: {eta}')
            send_delivery_to_telegram.apply_async(args=[delivery.id], eta=eta)

    except Exception as e:
        logger.error(f'Error checking deliveries: {e}')


@shared_task
def complete_task(task_id):
    logger.info(f'Completing task with id: {task_id}')
    try:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            logger.error(f'Task with id {task_id} does not exist.')
            return

        if task.is_completed:
            task.is_active = False
            task.save(update_fields=['is_active'])
            logger.info(f'Task {task_id} is already completed. Marking as inactive.')
        else:
            task.is_active = False
            task.is_completed = True
            task.save(update_fields=['is_completed', 'is_active'])
            logger.info(f'Task {task_id} marked as completed.')

    except Exception as e:
        logger.error(f'Error completing task: {e}')


@shared_task
def check_complete_task():
    logger.info('Checking for tasks to complete.')
    try:
        tasks = Task.objects.filter(end_date__date=timezone.make_aware(datetime.today()))
        logger.info(f'Found {len(tasks)} tasks to check for completion.')

        for task in tasks:
            eta = task.end_date + timedelta(hours=1)
            logger.info(f'Scheduling complete_task for task_id: {task.id} with ETA: {eta}')
            complete_task.apply_async(args=[task.id], eta=eta)

    except Exception as e:
        logger.error(f'Error checking for tasks to complete: {e}')


@shared_task
def duplicate_delivery_for_next_week():
    logger.info('Starting duplication of deliveries for the next week.')

    today = timezone.make_aware(datetime.today()).date()
    end_of_week = today + timedelta(days=(6 - today.weekday()))

    try:
        deliveries_to_duplicate = Delivery.objects.filter(
            date__range=(today, end_of_week),
        )
        logger.info(f'Found {len(deliveries_to_duplicate)} deliveries to duplicate.')

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
            logger.info(f'Duplicated delivery {delivery.id} to new delivery {new_delivery.id}.')
            new_delivery.save()

    except Exception as e:
        logger.error(f'Error during duplication process: {e}')
        return

    logger.info('All deliveries duplicated for the next week.')

import json
import zoneinfo
import requests
from datetime import timedelta, datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.contrib.auth import get_user_model
import httpx
import asyncio

from django.conf import settings
from .models import Task, Delivery


ZONE = zoneinfo.ZoneInfo(settings.TIME_ZONE)

User = get_user_model()

logger = get_task_logger('celery_log')

url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'


async def async_send_message(chat_id, message):
    payload = {'chat_id': chat_id, 'text': message}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
    return response


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_message_to_telegram(self, task_id, message):
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

    try:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(async_send_message(chat_id, message))

        if response.status_code == 200:
            logger.info(f'Message sent to {chat_id}: {message}')
        else:
            logger.error(f'Failed to send message to {chat_id}: {response.text}')
            raise Exception(f'Error from Telegram API: {response.text}')
    except Exception as e:
        logger.error(f'An error occurred while sending message to {chat_id}: {str(e)}')
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_massage_to_telegram_delivery(self, delivery_id, message):
    """
    Notification to the supervisor about a volunteer taking on a delivery.
    """
    logger.info(f'Starting send_message_to_telegram for task_id: {delivery_id}')

    try:
        delivery = Delivery.objects.get(id=delivery_id)
    except Delivery.DoesNotExist:
        logger.error(f"Delivery with id {delivery_id} does not exist.")
        return

    chat_id = delivery.curator.tg_id

    try:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(async_send_message(chat_id, message))

        if response.status_code == 200:
            logger.info(f'Message sent to {chat_id}: {message}')
        else:
            logger.error(f'Failed to send message to {chat_id}: {response.text}')
            raise Exception(f'Error from Telegram API: {response.text}')
    except Exception as e:
        logger.error(f'An error occurred while sending message to {chat_id}: {str(e)}')
        raise self.retry(exc=e)


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

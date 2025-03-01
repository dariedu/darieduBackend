import json
import requests
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import httpx
import asyncio

from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Promotion
from google_drive import GooglePromotion


User = get_user_model()

logger = logging.getLogger('celery_log')

url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'


async def async_send_message(chat_id, message):
    payload = {'chat_id': chat_id, 'text': message}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
    return response


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_message_to_telegrams(self, promotion_id, user):
    """
    Notifying the manager about the volunteer’s registration for incentives.
    """
    logger.info('send_message_to_telegrams', promotion_id)
    try:
        promo = Promotion.objects.get(id=promotion_id)
    except Promotion.DoesNotExist:
        logger.error(f'Promotion with id {promotion_id} does not exist.')
        return

    try:
        user = User.objects.get(id=user)
    except Exception as e:
        logger.error(f'Error getting user: {e}')
        return

    name = user.tg_username if user.tg_username else user.name
    contact_person = promo.contact_person
    chat_id = contact_person.tg_id

    message = f'Волонтер {name} записался на поощрение "{promo.name}"!'

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
def send_promotion_to_telegram(promotion_id):
    """
    Notification of confirmation of participation in task.
    """
    logger.info(f'Starting send_promotion_to_telegram for promotion_id: {promotion_id}')
    try:
        try:
            promotion = Promotion.objects.get(id=promotion_id)
        except Promotion.DoesNotExist:
            logger.error(f'Promotion with id {promotion_id} does not exist.')
            return
        volunteer_tg_ids = [user.tg_id for user in promotion.users.all()]
        timedate = promotion.start_date
        date_str = timedate.strftime('%d.%m.%Y')
        time_str = timedate.strftime('%H:%M')
        promotion_name = promotion.name
        data = {
            'promotion_id': promotion_id,
        }
        messages = f'Подтвердите вашу запись на "{promotion_name}" {date_str} в {time_str}!'
        keyboard = keyboard_promotion(data)
        logger.info('keyboard for promotion', keyboard)
        reply_markup = json.dumps(keyboard)
        for volunteer_tg_id in volunteer_tg_ids:
            payload = {
                'chat_id': volunteer_tg_id,
                'text': messages,
                'reply_markup': reply_markup
            }
            requests.post(url, json=payload)
    except Exception as e:
        logger.error(f'Error sending promotion to Telegram: {e}')


def keyboard_promotion(data):
    try:
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Подтвердить использование", "callback_data": f"accept_promotion:{json.dumps(data)}"},
                    {"text": "Отказаться", "callback_data": f'refuse_promotion:{json.dumps(data)}'}
                ]
            ]
        }
        return inline_keyboard
    except Exception as e:
        logger.error(f'Error creating keyboard: {e}')


@shared_task
def check_promotions():
    logger.info('Checking promotions')
    try:
        today = timezone.make_aware(datetime.today())
        logger.info(f'Checking promotions for date: {today.date()}')

        promotions = Promotion.objects.filter(start_date__date=today)
        # pprint(promotions)
        for promotion in promotions:
            eta = promotion.start_date - timedelta(hours=3)
            logger.info(f'Scheduling send_promotion_to_telegram for promotion_id: {promotion.id} with ETA: {eta}')
            if eta < timezone.make_aware(datetime.today()).replace(hour=9, minute=0, second=0, microsecond=0):
                eta = timezone.make_aware(datetime.today()).replace(hour=9, minute=5, second=0, microsecond=0)
                logger.info(f'Setting ETA for promotion {promotion.id} to {eta}')
            if eta >= timezone.make_aware(datetime.today()):
                send_promotion_to_telegram.apply_async(args=[promotion.id], eta=eta)
                logger.info(f'Scheduled send_promotion_to_telegram for promotion_id: {promotion.id} with ETA: {eta}')
    except Exception as e:
        logger.error(f'Error checking promotions: {e}')


@shared_task
def complete_promotion(promotion_id):
    logger.info(f'Completing promotion with id: {promotion_id}')
    try:
        promotion = Promotion.objects.get(id=promotion_id)
        logger.info(f'Completed promotion with id: {promotion_id}')
        promotion.is_active = False
        promotion.save()
    except Exception as e:
        logger.error(f'Error completing promotion: {e}')


@shared_task
def check_complete_promotion():
    logger.info('Checking promotions for completion')
    try:
        promotions = (Promotion.objects.filter(is_permanent=False).filter
                      (end_date__date=timezone.make_aware(datetime.today())))
        logger.info(f'Found {len(promotions)} promotions for completion')

        for promotion in promotions:
            eta = promotion.end_date + timedelta(hours=2)
            complete_promotion.apply_async(args=[promotion.id], eta=eta)
            logger.info(f'Scheduled complete_promotion for promotion_id: {promotion.id} with ETA: {eta}')

    except Exception as e:
        logger.error(f'Error checking promotions for completion: {e}')


@shared_task
def event_start_promotion(promotion_pk):
    logger.info(f'Event start promotion with id: {promotion_pk}')
    try:
        promotion = Promotion.objects.get(pk=promotion_pk)
        logger.info(f'Event start promotion with id: {promotion_pk}')
        participants = promotion.participation_set.filter(is_active=True)
        logger.info(f'Found {len(participants)} participants')
        google_promotion = GooglePromotion()
        links = google_promotion.get_links(promotion.ticket_file)  # Если будет ссылка, заменить на show_tickets(link=promotion.ticket_file)
        for participant, link in zip(participants, links):
            payload = {
                'chat_id': participant.user.tg_id,
                'text': f'Ваша билет: {link}'
            }
            response = requests.post(url, json=payload)
            logger.info(f'Event start promotion with id: {promotion_pk}')

    except Exception as e:
        logger.error(f'Error event start promotion: {e}')

import json
from datetime import datetime, timedelta
from pprint import pprint
from django.utils import timezone
from django.conf import settings

import requests
from celery import shared_task

from .models import Promotion


url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'

@shared_task
def send_promotion_to_telegram(promotion_id):
    """
    Notification of confirmation of participation in task.
    """
    promotion = Promotion.objects.get(id=promotion_id)
    volunteer_tg_ids = [user.tg_id for user in promotion.users.all()]
    timedate = promotion.start_date
    timedate = timedate.strftime('%d.%m.%Y %H:%M')
    promotion_name = promotion.name
    data = {
        'promotion_id': promotion_id,
    }
    messages = f'Подтвердите использование поощрения {promotion_name}, сегодня в {timedate}!'
    keyboard = keyboard_promotion(data)
    reply_markup = json.dumps(keyboard)
    for volunteer_tg_id in volunteer_tg_ids:
        payload = {
            'chat_id': volunteer_tg_id,
            'text': messages,
            'reply_markup': reply_markup
        }
        response = requests.post(url, json=payload)
        pprint(response.json())

def keyboard_promotion(data):
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "Подтвердить использование", "callback_data": "accept_promotion"},
                {"text": "Отказаться", "callback_data": f'refuse_promotion:{json.dumps(data)}'}
            ]
        ]
    }
    return inline_keyboard

@shared_task
def check_promotions():
    today = timezone.make_aware(datetime.today())
    promotions = Promotion.objects.filter(start_date__date=today)
    pprint(promotions)
    for promotion in promotions:
        eta = promotion.start_date - timedelta(hours=3)
        pprint(eta)
        if eta >= timezone.now():
            send_promotion_to_telegram.apply_async(args=[promotion.id], eta=eta)

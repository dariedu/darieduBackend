import json
import requests

from datetime import datetime, timedelta
from pprint import pprint
from django.utils import timezone
from django.conf import settings

from celery import shared_task

from .models import Promotion
from google_drive import GooglePromotion


url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'

@shared_task
def send_message_to_telegrams(promotion_id):
    """
    Notifying the manager about the volunteer’s registration for incentives.
    """
    promo = Promotion.objects.get(id=promotion_id)
    contact_person = promo.contact_person
    chat_id = contact_person.tg_id
    volunteers = promo.users.all()
    if volunteers.exists():
        name = volunteers.first().tg_username
        message = f'Волонтер {name} записался на поощрение "{promo.name}"!'
        payload = {'chat_id': chat_id, 'text': message}
        response = requests.post(url, json=payload)
        return response.json()


@shared_task
def send_promotion_to_telegram(promotion_id):
    """
    Notification of confirmation of participation in task.
    """
    promotion = Promotion.objects.get(id=promotion_id)
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
                {"text": "Подтвердить использование", "callback_data": f"accept_promotion:{json.dumps(data)}"},
                {"text": "Отказаться", "callback_data": f'refuse_promotion:{json.dumps(data)}'}
            ]
        ]
    }
    return inline_keyboard


@shared_task
def check_promotions():
    today = timezone.make_aware(datetime.today())
    promotions = Promotion.objects.filter(start_date__date=today)
    # pprint(promotions)
    for promotion in promotions:
        eta = promotion.start_date - timedelta(hours=3)
        if eta < timezone.make_aware(datetime.today()).replace(hour=9, minute=0, second=0, microsecond=0):
            eta = timezone.make_aware(datetime.today()).replace(hour=9, minute=5, second=0, microsecond=0)
        # pprint(eta)
        if eta >= timezone.make_aware(datetime.today()):
            send_promotion_to_telegram.apply_async(args=[promotion.id], eta=eta)


@shared_task
def complete_promotion(promotion_id):
    promotion = Promotion.objects.get(id=promotion_id)
    promotion.is_active = False
    promotion.save()


@shared_task
def check_complete_promotion():
    promotions = (Promotion.objects.filter(is_permanent=False).filter
                  (end_date__date=timezone.make_aware(datetime.today())))

    for promotion in promotions:
        eta = promotion.end_date + timedelta(hours=2)
        complete_promotion.apply_async(args=[promotion.id], eta=eta)


@shared_task
def event_start_promotion(promotion_pk):

    promotion = Promotion.objects.get(pk=promotion_pk)
    participants = promotion.participation_set.filter(is_active=True)
    google_promotion = GooglePromotion()
    links = google_promotion.get_links(promotion.ticket_file)  # Если будет ссылка, заменить на show_tickets(link=promotion.ticket_file)
    for participant, link in zip(participants, links):
        payload = {
            'chat_id': participant.user.tg_id,
            'text': f'Ваша билет: {link}'
        }
        response = requests.post(url, json=payload)

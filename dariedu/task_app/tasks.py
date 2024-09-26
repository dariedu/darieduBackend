import requests
from celery import shared_task
from django.conf import settings
from celery.utils.log import get_task_logger
from .models import Task

logger = get_task_logger(__name__)


@shared_task
def send_message_to_telegram(task_id):
    """
    Notification to the supervisor about a volunteer taking on a task.
    """
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    task = Task.objects.get(id=task_id)
    curator = task.curator
    chat_id = curator.tg_id
    volunteers = task.volunteers
    name = volunteers.first().name
    message = f"User {name} has signed up for task {task.name}!"
    payload = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, json=payload)
    return response.json()

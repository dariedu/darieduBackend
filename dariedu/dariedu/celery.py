import logging
import os
from celery import Celery
from celery.schedules import crontab

logging.basicConfig(level=logging.INFO)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dariedu.settings')

app = Celery('dariedu')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()

app.conf.timezone = 'Europe/Moscow'
app.conf.beat_schedule = {
    'check_deliveries_and_send_notifications': {
        'task': 'task_app.tasks.check_deliveries',
        'schedule': crontab(minute='00', hour='09'),
    },
    'send-check-tasks-to-telegram': {
        'task': 'task_app.tasks.check_tasks',
        'schedule': crontab(minute='00', hour='09'),
    },
    'send-promotion-to-telegram': {
        'task': 'promo_app.tasks.check_promotions',
        'schedule': crontab(minute='00', hour='08'),
    },
    'complete-task': {
        'task': 'task_app.tasks.check_complete_task',
        'schedule': crontab(minute='00', hour='12'),
    },
    'complete-delivery': {
        'task': 'promo_app.tasks.check_complete_delivery',
        'schedule': crontab(minute='00', hour='12'),
    },
    'complete-promotion': {
        'task': 'promo_app.tasks.check_complete_promotion',
        'schedule': crontab(minute='00', hour='12'),
    },
    'activate-delivery': {
        'task': 'promo_app.tasks.check_activate_delivery',
        'schedule': crontab(minute='00', hour='10'),
    },
}

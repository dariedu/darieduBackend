import logging
import os
from celery import Celery
from celery.schedules import crontab

logging.basicConfig(level=logging.INFO)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dariedu.settings')

app = Celery('dariedu')
# app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()


# @app.task(bind=True, ignore_result=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
#     logging.info(f'Task every 3 minutes')


app.conf.timezone = 'Europe/Moscow'
app.conf.beat_schedule = {
    # 'debug-task-every-3-minutes': {
    #     'task': 'dariedu.celery.debug_task',
    #     'schedule': 3.0,
    # },
    'check_deliveries_and_send_notifications': {
        'task': 'task_app.tasks.check_deliveries',
        'schedule': crontab(minute='00', hour='10'),
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
        'task': 'task_app.tasks.complete_task',
        'schedule': crontab(minute='00', hour='12'),
    },
    'complete-delivery': {
        'task': 'promo_app.tasks.complete_delivery',
        'schedule': crontab(minute='00', hour='12'),
    },
    'complete-promotion': {
        'task': 'promo_app.tasks.complete_promotion',
        'schedule': crontab(minute='00', hour='12'),
    },
}

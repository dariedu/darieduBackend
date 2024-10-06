import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dariedu.settings')

app = Celery('dariedu')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.timezone = 'Europe/Moscow'
app.conf.beat_schedule = {
    'check_deliveries_and_send_notifications': {
        'task': 'task_app.tasks.check_deliveries',
        'schedule': crontab(minute='00', hour='10'),
    },
    'send-check-tasks-to-telegram': {
        'task': 'task_app.tasks.check_tasks',
        'schedule': crontab(minute='02', hour='10'),
    },
    'send-promotion-to-telegram': {
        'task': 'promo_app.tasks.check_promotions',
        'schedule': crontab(minute='03', hour='17'),
    },
}

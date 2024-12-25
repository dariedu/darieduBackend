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
        'schedule': crontab(minute='00', hour='06'),
    },
    'send-check-tasks-to-telegram': {
        'task': 'task_app.tasks.check_tasks',
        'schedule': crontab(minute='00', hour='06'),
    },
    'send-promotion-to-telegram': {
        'task': 'promo_app.tasks.check_promotions',
        'schedule': crontab(minute='00', hour='06'),
    },
    'complete-task': {
        'task': 'task_app.tasks.check_complete_task',
        'schedule': crontab(minute='00', hour='12'),
    },
    'complete-delivery': {
        'task': 'task_app.tasks.check_complete_delivery',
        'schedule': crontab(minute='00', hour='12'),
    },
    'complete-promotion': {
        'task': 'promo_app.tasks.check_complete_promotion',
        'schedule': crontab(minute='00', hour='12'),
    },
    'activate-delivery': {
        'task': 'task_app.tasks.check_activate_delivery',
        'schedule': crontab(minute='00', hour='09'),
    },
    'duplicate-delivery-every-friday': {
        'task': 'task_app.tasks.duplicate_deliveries_for_next_week',
        'schedule': crontab(hour='10', minute='0', day_of_week='5'),
    },
    'backup-database-every-day': {
        'task': 'user_app.tasks.backup_database',
        'schedule': crontab(hour='20', minute='52'),
    },
    'delete-cached-gsheets-every-day': {
        'task': 'user_app.tasks.delete_cached_gsheets',
        'schedule': crontab(hour='02', minute='00'),
    },
    'update-ratings': {
        'task': 'user_app.tasks.update_ratings',
        'schedule': crontab(hour='02', minute='00'),
    },
    'update-volunteer-stats-minutely': {
        'task': 'statistics_app.tasks.update_statistics',
        'schedule': crontab('*'),
    },
    'update-all-statistics': {
        'task': 'statistics_app.tasks.all_statistics',
        'schedule': crontab('*'),
    },
}

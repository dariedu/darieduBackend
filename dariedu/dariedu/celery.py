import logging
import os
from celery import Celery
from celery.schedules import crontab

# from dariedu.settings import TIME_ZONE

logger = logging.getLogger('celery_log.beat')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dariedu.settings')

app = Celery('dariedu')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()

app.conf.timezone = 'Europe/Moscow'
app.conf.beat_schedule = {
    'complete-task': {
        'task': 'task_app.tasks.check_complete_task',
        'schedule': crontab(minute='00', hour='12'),
    },
    'complete-promotion': {
        'task': 'promo_app.tasks.check_complete_promotion',
        'schedule': crontab(minute='00', hour='12'),
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
    # 'update-volunteer-stats-minutely': {
    #     'task': 'statistics_app.tasks.update_statistics',
    #     'schedule': crontab(minute=0),
    # },
    # 'update-all-statistics': {
    #     'task': 'statistics_app.tasks.all_statistics',
    #     'schedule': crontab(minute=0),
    # },
    'check-users': {
        'task': 'user_app.tasks.check_users_task',
        'schedule': crontab(hour=17, minute=00, day_of_week='tue'),
    },
}


@app.task(bind=True)
def debug_task(self):
    logger.debug(f'Request: {self.request!r}')

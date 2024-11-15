from django.apps import AppConfig


class StatisticsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'statistics_app'
    verbose_name = 'Статистика'

    def ready(self):
        import statistics_app.signals

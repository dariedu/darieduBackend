from django.apps import AppConfig


class TaskAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_app'

    def ready(self):
        import task_app.schema

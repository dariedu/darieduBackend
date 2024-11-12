from django.apps import AppConfig


class AddressAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'address_app'

    def ready(self):
        import address_app.signals

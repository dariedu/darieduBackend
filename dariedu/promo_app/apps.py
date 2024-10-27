from django.apps import AppConfig

class PromoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'promo_app'

    def ready(self):
        import promo_app.schema
        import promo_app.signal

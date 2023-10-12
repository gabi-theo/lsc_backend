from django.apps import AppConfig


class RecuperariConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recuperari'

    def ready(self):
        import recuperari.signals

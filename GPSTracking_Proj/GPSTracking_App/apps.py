from django.apps import AppConfig


class GpstrackingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'GPSTracking_App'

    def ready(self):
        import GPSTracking_App.signals
from django.apps import AppConfig


class EventServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.event_service"
    label = "event_service"
    verbose_name = "Events"


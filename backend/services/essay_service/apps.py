from django.apps import AppConfig


class EssayServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.essay_service"
    label = "essay_service"
    verbose_name = "Essay feedback"


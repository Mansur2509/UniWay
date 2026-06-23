from django.apps import AppConfig


class AuthServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.auth_service"
    label = "auth_service"
    verbose_name = "Identity and access"


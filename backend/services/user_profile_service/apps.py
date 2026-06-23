from django.apps import AppConfig


class UserProfileServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.user_profile_service"
    label = "user_profile_service"
    verbose_name = "Student profiles"


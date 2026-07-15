from django.apps import AppConfig


class TelegramServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.telegram_service"
    label = "telegram_service"
    verbose_name = "Telegram integration"

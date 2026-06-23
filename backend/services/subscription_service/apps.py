from django.apps import AppConfig


class SubscriptionServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.subscription_service"
    label = "subscription_service"
    verbose_name = "Subscriptions and usage"


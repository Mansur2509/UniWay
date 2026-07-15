from django.urls import path

from .views import (
    TelegramLinkStatusView,
    TelegramLinkTokenView,
    TelegramMiniAppSessionView,
    TelegramWebhookView,
)

app_name = "telegram"

urlpatterns = [
    path("link/", TelegramLinkStatusView.as_view(), name="link-status"),
    path("link-token/", TelegramLinkTokenView.as_view(), name="link-token"),
    path("webhook/", TelegramWebhookView.as_view(), name="webhook"),
    path("mini-app/session/", TelegramMiniAppSessionView.as_view(), name="mini-app-session"),
]

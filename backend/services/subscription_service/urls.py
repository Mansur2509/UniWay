from django.urls import path

from .views import (
    BillingCancelView,
    BillingCheckoutSessionView,
    BillingHistoryView,
    BillingWebhookView,
)

urlpatterns = [
    path("checkout-session/", BillingCheckoutSessionView.as_view(), name="billing-checkout-session"),
    path("webhook/", BillingWebhookView.as_view(), name="billing-webhook"),
    path("cancel/", BillingCancelView.as_view(), name="billing-cancel"),
    path("history/", BillingHistoryView.as_view(), name="billing-history"),
]

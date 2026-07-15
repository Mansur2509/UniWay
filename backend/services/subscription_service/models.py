from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.TextChoices):
    FREE = "free", "Free"
    STARTER = "starter", "$5"
    GROWTH = "growth", "$10"
    PREMIUM = "premium", "$25"


class Subscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE, db_index=True)
    period_started_at = models.DateTimeField(default=timezone.now)
    ai_message_count = models.PositiveIntegerField(default=0)
    essay_review_count = models.PositiveIntegerField(default=0)
    saved_events_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class UsageLimit(models.Model):
    plan = models.CharField(max_length=20, choices=Plan.choices, unique=True)
    ai_messages_per_month = models.PositiveIntegerField(default=5)
    essay_reviews_per_month = models.PositiveIntegerField(default=1)
    saved_events = models.PositiveIntegerField(default=25)
    feature_flags = models.JSONField(default=dict, blank=True)


class UsageLog(models.Model):
    class Kind(models.TextChoices):
        AI_MESSAGE = "ai_message", "AI message"
        ESSAY_REVIEW = "essay_review", "Essay review"
        SAVED_EVENT = "saved_event", "Saved event"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="usage_logs")
    kind = models.CharField(max_length=30, choices=Kind.choices, db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


# POST-V1-021 Phase 9: billing/entitlement architecture. Sandbox-ready only
# -- no live payment provider is integrated (no credentials, no legal/
# pricing decision made). Nothing here activates a real charge; see
# docs/POST_V1_PRODUCT_ROADMAP_021.md Module F for what remains before a
# live launch (provider choice, legal review, production API keys).


class BillingCustomer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="billing_customer"
    )
    provider = models.CharField(max_length=30, default="sandbox")
    provider_customer_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BillingRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="billing_records"
    )
    provider = models.CharField(max_length=30, default="sandbox")
    provider_invoice_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    plan = models.CharField(max_length=20, choices=Plan.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class WebhookEvent(models.Model):
    """Every inbound webhook is recorded, keyed by the provider's own event
    id, before any side effect is applied -- a retried webhook delivery
    (which every real provider does) is a no-op the second time. This is
    the idempotency mechanism itself, not a side effect of it."""

    provider = models.CharField(max_length=30)
    provider_event_id = models.CharField(max_length=120)
    event_type = models.CharField(max_length=60)
    payload = models.JSONField()
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("provider", "provider_event_id"), name="unique_webhook_event_per_provider"
            )
        ]


class SubscriptionCancellation(models.Model):
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="cancellations"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    effective_at = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True)


class BillingAuditLogEntry(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    action = models.CharField(max_length=60)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)


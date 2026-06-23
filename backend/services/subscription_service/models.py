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


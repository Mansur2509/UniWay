from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Subscription


@transaction.atomic
def reset_usage_if_period_elapsed(subscription: Subscription) -> Subscription:
    if timezone.now() < subscription.period_started_at + timedelta(days=30):
        return subscription

    subscription.period_started_at = timezone.now()
    subscription.ai_message_count = 0
    subscription.essay_review_count = 0
    subscription.saved_events_count = 0
    subscription.save(
        update_fields=[
            "period_started_at",
            "ai_message_count",
            "essay_review_count",
            "saved_events_count",
            "updated_at",
        ]
    )
    return subscription


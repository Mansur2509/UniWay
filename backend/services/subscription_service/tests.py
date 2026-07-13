from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Plan, Subscription

User = get_user_model()


class SubscriptionApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="subscription-reader@example.com",
            email="subscription-reader@example.com",
            password="Strong-Development-Password-842!",
        )
        self.client.force_authenticate(self.user)

    def test_me_does_not_create_missing_subscription_on_get(self):
        response = self.client.get("/api/v1/subscriptions/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["plan"], Plan.FREE)
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())

    def test_elapsed_period_is_reset_for_display_without_get_write(self):
        started_at = timezone.now() - timedelta(days=31)
        subscription = Subscription.objects.create(
            user=self.user,
            period_started_at=started_at,
            ai_message_count=4,
            essay_review_count=2,
            saved_events_count=3,
        )

        response = self.client.get("/api/v1/subscriptions/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ai_message_count"], 0)
        subscription.refresh_from_db()
        self.assertEqual(subscription.period_started_at, started_at)
        self.assertEqual(subscription.ai_message_count, 4)

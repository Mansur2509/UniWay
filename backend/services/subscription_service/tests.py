import hashlib
import hmac
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import (
    BillingAuditLogEntry,
    BillingRecord,
    Plan,
    Subscription,
    SubscriptionCancellation,
    UsageLimit,
    WebhookEvent,
)

User = get_user_model()
STRONG_PASSWORD = "Strong-Development-Password-842!"
WEBHOOK_SECRET = "test-only-billing-webhook-secret"


def _signed_webhook_body(payload: dict) -> tuple[bytes, str]:
    body = json.dumps(payload).encode()
    signature = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return body, signature


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


class CheckoutSessionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer@example.com", email="buyer@example.com", password=STRONG_PASSWORD
        )

    def test_checkout_session_is_sandbox_only_and_never_live(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/v1/billing/checkout-session/", {"plan": Plan.STARTER}, format="json"
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertFalse(response.data["is_live"])
        self.assertTrue(response.data["checkout_url"].startswith("https://sandbox."))
        self.assertTrue(
            BillingRecord.objects.filter(
                user=self.user, status=BillingRecord.Status.PENDING
            ).exists()
        )
        self.assertTrue(
            BillingAuditLogEntry.objects.filter(
                actor=self.user, action="checkout_session_created"
            ).exists()
        )

    def test_checkout_session_rejects_an_unauthenticated_caller(self):
        response = self.client.post(
            "/api/v1/billing/checkout-session/", {"plan": Plan.STARTER}, format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_checkout_session_rejects_the_free_plan(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/v1/billing/checkout-session/", {"plan": Plan.FREE}, format="json"
        )

        self.assertEqual(response.status_code, 400)


class WebhookSignatureTests(APITestCase):
    def _payload(self, event_id="evt_signature_test"):
        return {
            "provider": "sandbox",
            "event_id": event_id,
            "event_type": "invoice.paid",
            "payload": {},
        }

    def test_missing_signature_is_rejected_before_reaching_webhookevent(self):
        with override_settings(BILLING_WEBHOOK_SECRET=WEBHOOK_SECRET):
            body, _ = _signed_webhook_body(self._payload())
            response = self.client.post(
                "/api/v1/billing/webhook/", data=body, content_type="application/json"
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(WebhookEvent.objects.count(), 0)

    def test_badly_signed_payload_is_rejected_before_reaching_webhookevent(self):
        with override_settings(BILLING_WEBHOOK_SECRET=WEBHOOK_SECRET):
            body, _ = _signed_webhook_body(self._payload())
            response = self.client.post(
                "/api/v1/billing/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_BILLING_SIGNATURE="0" * 64,
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(WebhookEvent.objects.count(), 0)

    def test_an_unconfigured_secret_rejects_every_request_even_a_well_formed_one(self):
        body, signature = _signed_webhook_body(self._payload())

        response = self.client.post(
            "/api/v1/billing/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_BILLING_SIGNATURE=signature,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(WebhookEvent.objects.count(), 0)

    def test_correctly_signed_payload_is_processed(self):
        with override_settings(BILLING_WEBHOOK_SECRET=WEBHOOK_SECRET):
            body, signature = _signed_webhook_body(self._payload())
            response = self.client.post(
                "/api/v1/billing/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_BILLING_SIGNATURE=signature,
            )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(WebhookEvent.objects.count(), 1)


class WebhookIdempotencyAndFulfillmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="payer@example.com", email="payer@example.com", password=STRONG_PASSWORD
        )

    def test_duplicate_event_id_results_in_exactly_one_fulfillment(self):
        BillingRecord.objects.create(
            user=self.user,
            provider="sandbox",
            provider_invoice_id="sandbox_inv_duplicate_test",
            amount=5,
            plan=Plan.STARTER,
            status=BillingRecord.Status.PENDING,
        )
        payload = {
            "provider": "sandbox",
            "event_id": "evt_duplicate_delivery",
            "event_type": "invoice.paid",
            "payload": {"invoice_id": "sandbox_inv_duplicate_test", "status": "succeeded"},
        }
        body, signature = _signed_webhook_body(payload)

        with override_settings(BILLING_WEBHOOK_SECRET=WEBHOOK_SECRET):
            first = self.client.post(
                "/api/v1/billing/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_BILLING_SIGNATURE=signature,
            )
            second = self.client.post(
                "/api/v1/billing/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_BILLING_SIGNATURE=signature,
            )

        self.assertEqual(first.status_code, 200, first.data)
        self.assertEqual(second.status_code, 200, second.data)
        self.assertEqual(first.data["status"], "processed")
        self.assertEqual(second.data["status"], "already_processed")
        self.assertEqual(
            WebhookEvent.objects.filter(provider_event_id="evt_duplicate_delivery").count(), 1
        )
        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(subscription.plan, Plan.STARTER)

    def test_a_refund_transitions_an_existing_record_to_refunded(self):
        BillingRecord.objects.create(
            user=self.user,
            provider="sandbox",
            provider_invoice_id="sandbox_inv_refund_test",
            amount=5,
            plan=Plan.STARTER,
            status=BillingRecord.Status.SUCCEEDED,
        )
        payload = {
            "provider": "sandbox",
            "event_id": "evt_refund",
            "event_type": "invoice.refunded",
            "payload": {"invoice_id": "sandbox_inv_refund_test", "status": "refunded"},
        }
        body, signature = _signed_webhook_body(payload)

        with override_settings(BILLING_WEBHOOK_SECRET=WEBHOOK_SECRET):
            response = self.client.post(
                "/api/v1/billing/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_BILLING_SIGNATURE=signature,
            )

        self.assertEqual(response.status_code, 200, response.data)
        record = BillingRecord.objects.get(provider_invoice_id="sandbox_inv_refund_test")
        self.assertEqual(record.status, BillingRecord.Status.REFUNDED)


class CancellationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="canceller@example.com", email="canceller@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(self.user)

    def test_cancelling_with_no_active_paid_plan_is_rejected(self):
        response = self.client.post("/api/v1/billing/cancel/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(SubscriptionCancellation.objects.count(), 0)

    def test_cancelling_a_paid_plan_sets_a_future_effective_date_without_downgrading(self):
        Subscription.objects.create(user=self.user, plan=Plan.GROWTH)

        response = self.client.post(
            "/api/v1/billing/cancel/", {"reason": "Too expensive"}, format="json"
        )

        self.assertEqual(response.status_code, 201, response.data)
        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(subscription.plan, Plan.GROWTH)
        cancellation = SubscriptionCancellation.objects.get(subscription=subscription)
        self.assertGreater(cancellation.effective_at, timezone.now())
        self.assertTrue(
            BillingAuditLogEntry.objects.filter(
                actor=self.user, action="cancellation_requested"
            ).exists()
        )


class BillingHistoryTests(APITestCase):
    def test_history_only_returns_the_caller_s_own_records(self):
        owner = User.objects.create_user(
            username="owner@example.com", email="owner@example.com", password=STRONG_PASSWORD
        )
        other = User.objects.create_user(
            username="other@example.com", email="other@example.com", password=STRONG_PASSWORD
        )
        own_record = BillingRecord.objects.create(
            user=owner,
            provider_invoice_id="sandbox_inv_owner",
            amount=5,
            plan=Plan.STARTER,
            status=BillingRecord.Status.SUCCEEDED,
        )
        BillingRecord.objects.create(
            user=other,
            provider_invoice_id="sandbox_inv_other",
            amount=5,
            plan=Plan.STARTER,
            status=BillingRecord.Status.SUCCEEDED,
        )
        self.client.force_authenticate(owner)

        response = self.client.get("/api/v1/billing/history/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_record.id)


class EntitlementEnforcementTests(APITestCase):
    def test_plan_upgrade_via_webhook_changes_the_limits_the_me_endpoint_reports(self):
        user = User.objects.create_user(
            username="upgrader@example.com", email="upgrader@example.com", password=STRONG_PASSWORD
        )
        UsageLimit.objects.create(
            plan=Plan.FREE, ai_messages_per_month=5, essay_reviews_per_month=1, saved_events=25
        )
        UsageLimit.objects.create(
            plan=Plan.GROWTH, ai_messages_per_month=200, essay_reviews_per_month=20, saved_events=500
        )
        BillingRecord.objects.create(
            user=user,
            provider_invoice_id="sandbox_inv_upgrade",
            amount=10,
            plan=Plan.GROWTH,
            status=BillingRecord.Status.PENDING,
        )
        payload = {
            "provider": "sandbox",
            "event_id": "evt_upgrade",
            "event_type": "invoice.paid",
            "payload": {"invoice_id": "sandbox_inv_upgrade", "status": "succeeded"},
        }
        body, signature = _signed_webhook_body(payload)

        with override_settings(BILLING_WEBHOOK_SECRET=WEBHOOK_SECRET):
            webhook_response = self.client.post(
                "/api/v1/billing/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_BILLING_SIGNATURE=signature,
            )
        self.assertEqual(webhook_response.status_code, 200, webhook_response.data)

        self.client.force_authenticate(user)
        me_response = self.client.get("/api/v1/subscriptions/me/")

        self.assertEqual(me_response.data["plan"], Plan.GROWTH)
        self.assertEqual(me_response.data["limits"]["essay_reviews_per_month"], 20)

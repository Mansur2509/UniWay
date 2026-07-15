"""Billing/entitlement architecture (POST-V1-021 Phase 9).

Sandbox-ready only. No real payment provider is integrated -- there is no
provider API key, no legal/pricing review, and no live checkout button.
Every function here is safe to call in any environment because nothing
here ever reaches a real external payment network.
"""

from __future__ import annotations

import hashlib
import hmac
import uuid

from django.conf import settings
from django.utils import timezone

from .models import (
    BillingAuditLogEntry,
    BillingCustomer,
    BillingRecord,
    Subscription,
    SubscriptionCancellation,
    WebhookEvent,
)

SANDBOX_PROVIDER = "sandbox"
CANCELLATION_NOTICE_DAYS = 30


def is_webhook_signing_configured() -> bool:
    return bool(settings.BILLING_WEBHOOK_SECRET)


def verify_webhook_signature(*, payload_body: bytes, provided_signature: str) -> bool:
    """Constant-time HMAC-SHA256 verification over the exact raw request
    body, the same shape as a real provider's webhook signature (e.g.
    Stripe). Fails closed: a missing signature, an unconfigured secret, or a
    mismatched digest are all rejected identically, so the caller never
    reaches WebhookEvent for anything that isn't genuinely signed."""
    if not is_webhook_signing_configured() or not provided_signature:
        return False
    expected = hmac.new(
        settings.BILLING_WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, provided_signature)


def _get_or_create_billing_customer(user) -> BillingCustomer:
    customer, _ = BillingCustomer.objects.get_or_create(
        user=user,
        defaults={
            "provider": SANDBOX_PROVIDER,
            "provider_customer_id": f"sandbox_cust_{uuid.uuid4().hex[:20]}",
        },
    )
    return customer


def create_sandbox_checkout_session(*, user, plan: str) -> dict:
    """Never a real charge: this only records a PENDING BillingRecord and
    returns a clearly-labeled sandbox URL. No provider API key is read or
    required; the actual sandbox `checkout_url` here does not resolve to
    any real payment page."""
    _get_or_create_billing_customer(user)
    invoice_id = f"sandbox_inv_{uuid.uuid4().hex[:24]}"
    record = BillingRecord.objects.create(
        user=user,
        provider=SANDBOX_PROVIDER,
        provider_invoice_id=invoice_id,
        amount=0,
        plan=plan,
        status=BillingRecord.Status.PENDING,
    )
    return {
        "checkout_url": f"https://sandbox.uniway.local/checkout/{invoice_id}",
        "billing_record_id": record.id,
        "is_live": False,
    }


def process_webhook_event(*, provider: str, event_id: str, event_type: str, payload: dict) -> dict:
    """Idempotent: the same (provider, event_id) processed twice results in
    exactly one side effect, because the second call's `get_or_create`
    finds the already-`processed_at`-stamped row and returns immediately."""
    event, created = WebhookEvent.objects.get_or_create(
        provider=provider,
        provider_event_id=event_id,
        defaults={"event_type": event_type, "payload": payload},
    )
    if not created and event.processed_at is not None:
        return {"status": "already_processed", "event_id": event.id}

    invoice_id = payload.get("invoice_id")
    new_status = payload.get("status")
    if invoice_id and new_status in BillingRecord.Status.values:
        BillingRecord.objects.filter(provider_invoice_id=invoice_id).update(status=new_status)
        if new_status == BillingRecord.Status.SUCCEEDED:
            record = BillingRecord.objects.filter(provider_invoice_id=invoice_id).first()
            if record is not None:
                Subscription.objects.update_or_create(
                    user=record.user, defaults={"plan": record.plan}
                )

    event.processed_at = timezone.now()
    event.save(update_fields=["processed_at"])
    return {"status": "processed", "event_id": event.id}


def request_cancellation(*, subscription: Subscription, reason: str = "") -> SubscriptionCancellation:
    """Cancellation takes effect at the end of the notice period, not
    immediately -- a cancelling user keeps their current plan's access
    until then. Never downgrades `subscription.plan` here."""
    effective_at = timezone.now() + timezone.timedelta(days=CANCELLATION_NOTICE_DAYS)
    return SubscriptionCancellation.objects.create(
        subscription=subscription, effective_at=effective_at, reason=reason
    )


def log_billing_action(*, actor, action: str, target_user=None, metadata=None) -> None:
    BillingAuditLogEntry.objects.create(
        actor=actor, action=action, target_user=target_user, metadata=metadata or {}
    )

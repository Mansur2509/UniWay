"""Telegram Bot / Mini App foundation (POST-V1-021 Phase 5).

Every function here is safe to call whether or not `TELEGRAM_BOT_TOKEN` is
configured; live-bot-only operations check `is_telegram_configured()` first
so the rest of the app never has to know whether Telegram is live.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import parse_qsl

from django.conf import settings
from django.utils import timezone

from .models import LINK_TOKEN_TTL_MINUTES, ReminderDelivery, TelegramLink, TelegramLinkToken

MINI_APP_INIT_DATA_MAX_AGE_SECONDS = 300


def is_telegram_configured() -> bool:
    return bool(settings.TELEGRAM_BOT_TOKEN)


def issue_link_token(user) -> TelegramLinkToken:
    """Idempotent-ish: invalidates the user's other unconsumed tokens first
    so only one active token exists, then issues a fresh one."""
    TelegramLinkToken.objects.filter(user=user, consumed_at__isnull=True).update(
        consumed_at=timezone.now()
    )
    return TelegramLinkToken.objects.create(user=user)


class LinkTokenError(Exception):
    """Raised for an invalid, expired, or already-consumed link token."""


def consume_link_token(*, token: str, telegram_user_id: int, telegram_username: str = "") -> TelegramLink:
    """Called only from the verified Telegram webhook handler, never from an
    unauthenticated HTTP endpoint directly -- the caller must already have
    confirmed this request genuinely came from Telegram (see
    `verify_webhook_secret`)."""
    link_token = TelegramLinkToken.objects.filter(token=token).first()
    if link_token is None or not link_token.is_valid():
        raise LinkTokenError("This link code is invalid or has expired.")

    existing_for_telegram_id = TelegramLink.objects.filter(
        telegram_user_id=telegram_user_id, unlinked_at__isnull=True
    ).exclude(user=link_token.user)
    if existing_for_telegram_id.exists():
        raise LinkTokenError("This Telegram account is already linked to a different UniWay account.")

    link_token.consumed_at = timezone.now()
    link_token.save(update_fields=["consumed_at"])

    link, _ = TelegramLink.objects.update_or_create(
        user=link_token.user,
        defaults={
            "telegram_user_id": telegram_user_id,
            "telegram_username": telegram_username,
            "unlinked_at": None,
        },
    )
    return link


def unlink_telegram(user) -> None:
    TelegramLink.objects.filter(user=user, unlinked_at__isnull=True).update(
        unlinked_at=timezone.now()
    )


def verify_webhook_secret(*, provided_secret: str) -> bool:
    """Compares the `X-Telegram-Bot-Api-Secret-Token` header (Telegram's own
    recommended webhook-authenticity mechanism) against our configured bot
    token, using a constant-time comparison to avoid timing side channels."""
    if not is_telegram_configured():
        return False
    return hmac.compare_digest(provided_secret or "", settings.TELEGRAM_BOT_TOKEN)


def verify_mini_app_init_data(init_data: str) -> dict | None:
    """Verifies a Telegram Mini App `initData` payload per Telegram's
    documented algorithm. Returns the parsed fields if genuinely signed by
    our bot token and recent enough; returns None otherwise. Never trusts
    an unsigned or stale payload, and never trusts a user id supplied any
    other way for Mini App requests."""
    if not is_telegram_configured() or not init_data:
        return None

    pairs = dict(parse_qsl(init_data, strict_parsing=False))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
    secret_key = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    auth_date = pairs.get("auth_date")
    if not auth_date or not auth_date.isdigit():
        return None
    if time.time() - int(auth_date) > MINI_APP_INIT_DATA_MAX_AGE_SECONDS:
        return None

    return pairs


def record_reminder_sent(*, user, related_entity_type: str, related_entity_id: int) -> bool:
    """Returns True if this call actually recorded a new send; False if a
    reminder for this exact (user, entity) was already sent (idempotent
    dispatch -- safe to call from a periodic job run more than once)."""
    _, created = ReminderDelivery.objects.get_or_create(
        user=user,
        channel=ReminderDelivery.Channel.TELEGRAM,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    return created


__all__ = [
    "LINK_TOKEN_TTL_MINUTES",
    "LinkTokenError",
    "consume_link_token",
    "is_telegram_configured",
    "issue_link_token",
    "record_reminder_sent",
    "unlink_telegram",
    "verify_mini_app_init_data",
    "verify_webhook_secret",
]

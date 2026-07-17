from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import PasswordResetToken

User = get_user_model()

PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS = 60 * 60


class PasswordResetError(Exception):
    code = "invalid"


class PasswordResetTokenInvalid(PasswordResetError):
    code = "invalid"


class PasswordResetTokenExpired(PasswordResetError):
    code = "expired"


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _reset_url(raw_token: str) -> str:
    separator = "&" if "?" in settings.PASSWORD_RESET_FRONTEND_URL else "?"
    return f"{settings.PASSWORD_RESET_FRONTEND_URL}{separator}{urlencode({'token': raw_token})}"


def request_password_reset(email: str) -> None:
    """Neutral by design: always returns without error whether or not the
    address belongs to an account, so callers can never distinguish the two
    cases from the response alone."""
    normalized_email = User.objects.normalize_email(email).lower()
    user = User.objects.filter(email__iexact=normalized_email, is_active=True).first()
    if user is None:
        return

    raw_token = secrets.token_urlsafe(32)
    PasswordResetToken.objects.create(
        user=user,
        token_digest=_digest(raw_token),
        expires_at=timezone.now() + timedelta(seconds=PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS),
    )
    send_mail(
        subject="Reset your UniWay password",
        message=(
            "We received a request to reset your UniWay password.\n\n"
            f"Reset it here (valid for 1 hour): {_reset_url(raw_token)}\n\n"
            "If you did not request this, you can safely ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def get_valid_reset_user(token: str):
    """Read-only lookup used for early, friendly validation errors. Does not
    mark the token used -- consume_password_reset_token is the authoritative,
    race-safe check that actually performs the reset."""
    try:
        record = PasswordResetToken.objects.select_related("user").get(token_digest=_digest(token))
    except PasswordResetToken.DoesNotExist as error:
        raise PasswordResetTokenInvalid from error
    if record.used_at is not None or not record.user.is_active:
        raise PasswordResetTokenInvalid
    if record.expires_at <= timezone.now():
        raise PasswordResetTokenExpired
    return record.user


@transaction.atomic
def consume_password_reset_token(token: str, new_password: str) -> None:
    try:
        record = PasswordResetToken.objects.select_for_update().select_related("user").get(
            token_digest=_digest(token)
        )
    except PasswordResetToken.DoesNotExist as error:
        raise PasswordResetTokenInvalid from error

    now = timezone.now()
    if record.used_at is not None or not record.user.is_active:
        raise PasswordResetTokenInvalid
    if record.expires_at <= now:
        raise PasswordResetTokenExpired

    record.user.set_password(new_password)
    record.user.save(update_fields=["password"])
    record.used_at = now
    record.save(update_fields=["used_at"])

    # A password reset is a strong signal that a prior session may be
    # compromised (that's often why someone resets it), so every outstanding
    # refresh token for this user is blacklisted, forcing re-login everywhere.
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

    for outstanding in OutstandingToken.objects.filter(user=record.user):
        BlacklistedToken.objects.get_or_create(token=outstanding)

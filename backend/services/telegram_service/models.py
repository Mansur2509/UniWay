import secrets

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

LINK_TOKEN_TTL_MINUTES = 10


def _generate_link_token() -> str:
    return secrets.token_urlsafe(24)


def _default_token_expiry():
    return timezone.now() + timezone.timedelta(minutes=LINK_TOKEN_TTL_MINUTES)


class TelegramLink(models.Model):
    """A verified link between a UniWay account and a Telegram user id.

    Never created directly from an unverified client-supplied id: only
    `consume_link_token` (services.py) may create one, after the student's
    own web session issued a `TelegramLinkToken` and the bot confirmed
    receiving it from that specific Telegram user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram_link"
    )
    telegram_user_id = models.BigIntegerField(db_index=True)
    telegram_username = models.CharField(max_length=64, blank=True)
    linked_at = models.DateTimeField(auto_now_add=True)
    unlinked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["telegram_user_id"],
                condition=Q(unlinked_at__isnull=True),
                name="unique_active_telegram_user_id",
            )
        ]

    def __str__(self) -> str:
        return f"TelegramLink(user={self.user_id}, tg={self.telegram_user_id})"


class TelegramLinkToken(models.Model):
    """Short-lived, single-use token a student pastes into the bot chat to
    prove they own both the web session and the Telegram account."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram_link_tokens"
    )
    token = models.CharField(max_length=64, unique=True, default=_generate_link_token)
    expires_at = models.DateTimeField(default=_default_token_expiry)
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self) -> bool:
        return self.consumed_at is None and self.expires_at > timezone.now()

    def __str__(self) -> str:
        return f"TelegramLinkToken(user={self.user_id}, consumed={self.consumed_at is not None})"


class ReminderDelivery(models.Model):
    """One row per reminder actually sent. The periodic dispatch job's own
    idempotency mechanism: it never re-sends a reminder already recorded
    here for the same (user, channel, entity)."""

    class Channel(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reminder_deliveries"
    )
    channel = models.CharField(max_length=20, choices=Channel.choices)
    related_entity_type = models.CharField(max_length=40)
    related_entity_id = models.PositiveIntegerField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "channel", "related_entity_type", "related_entity_id"],
                name="unique_reminder_per_entity_per_channel",
            )
        ]

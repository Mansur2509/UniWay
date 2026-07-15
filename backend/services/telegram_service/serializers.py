from rest_framework import serializers

from .models import TelegramLink, TelegramLinkToken


class TelegramLinkTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramLinkToken
        fields = ("token", "expires_at")
        read_only_fields = fields


class TelegramLinkStatusSerializer(serializers.Serializer):
    is_linked = serializers.BooleanField()
    telegram_username = serializers.CharField(allow_blank=True)
    linked_at = serializers.DateTimeField(allow_null=True)

    @classmethod
    def for_user(cls, user) -> "TelegramLinkStatusSerializer":
        link = TelegramLink.objects.filter(user=user, unlinked_at__isnull=True).first()
        return cls(
            {
                "is_linked": link is not None,
                "telegram_username": link.telegram_username if link else "",
                "linked_at": link.linked_at if link else None,
            }
        )


class TelegramWebhookMessageSerializer(serializers.Serializer):
    """Minimal shape this app actually reads from a Telegram Bot API
    "message" update -- not a full Bot API schema, since this foundation
    only needs to recognize a pasted link token."""

    message = serializers.DictField(required=False)

    def extract_link_attempt(self) -> tuple[int, str, str] | None:
        message = self.validated_data.get("message")
        if not message:
            return None
        text = (message.get("text") or "").strip()
        from_user = message.get("from") or {}
        telegram_user_id = from_user.get("id")
        if not text or telegram_user_id is None:
            return None
        return telegram_user_id, text, from_user.get("username", "")

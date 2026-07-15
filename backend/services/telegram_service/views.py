import json

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.throttling import ScopedIPRateThrottle
from services.auth_service.cookies import set_refresh_cookie
from services.auth_service.serializers import CurrentUserSerializer, token_pair_for_user

from .models import TelegramLink
from .serializers import (
    TelegramLinkStatusSerializer,
    TelegramLinkTokenSerializer,
    TelegramWebhookMessageSerializer,
)
from .services import (
    LinkTokenError,
    consume_link_token,
    is_telegram_configured,
    issue_link_token,
    unlink_telegram,
    verify_mini_app_init_data,
    verify_webhook_secret,
)

NOT_CONFIGURED_RESPONSE = {
    "detail": "Telegram is not configured on this deployment yet.",
    "telegram_configured": False,
}


class TelegramLinkStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = TelegramLinkStatusSerializer.for_user(request.user)
        return Response(serializer.data)

    def delete(self, request):
        unlink_telegram(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TelegramLinkTokenView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle, ScopedIPRateThrottle]
    throttle_scope = "telegram_link_token"

    def post(self, request):
        if not is_telegram_configured():
            return Response(NOT_CONFIGURED_RESPONSE, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        link_token = issue_link_token(request.user)
        return Response(TelegramLinkTokenSerializer(link_token).data, status=status.HTTP_201_CREATED)


class TelegramWebhookView(APIView):
    """Receives Telegram Bot API updates. Public by necessity (Telegram is
    the caller, not an authenticated UniWay user) -- authenticity is
    established entirely by the secret-token header, never by payload
    content alone."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle, ScopedIPRateThrottle]
    throttle_scope = "telegram_webhook"

    def post(self, request):
        if not is_telegram_configured():
            return Response(NOT_CONFIGURED_RESPONSE, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        provided_secret = request.META.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN", "")
        if not verify_webhook_secret(provided_secret=provided_secret):
            return Response({"detail": "Invalid webhook secret."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TelegramWebhookMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = serializer.extract_link_attempt()
        if attempt is None:
            return Response({"ok": True})

        telegram_user_id, text, username = attempt
        try:
            consume_link_token(token=text, telegram_user_id=telegram_user_id, telegram_username=username)
        except LinkTokenError:
            # Not every message is a link-code attempt -- silently
            # acknowledge rather than error, matching Telegram's own
            # expectation that webhooks always return 200 for handled updates.
            pass
        return Response({"ok": True})


class TelegramMiniAppSessionView(APIView):
    """Exchanges a verified Telegram Mini App `initData` payload for a
    normal UniWay session, for a Telegram user who has already linked their
    account via the bot. Never trusts a client-supplied user id -- only the
    HMAC-verified `initData` (see `verify_mini_app_init_data`)."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle, ScopedIPRateThrottle]
    throttle_scope = "telegram_mini_app_session"

    def post(self, request):
        if not is_telegram_configured():
            return Response(NOT_CONFIGURED_RESPONSE, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        init_data = request.data.get("init_data", "")
        verified = verify_mini_app_init_data(init_data)
        if verified is None:
            return Response(
                {"detail": "Telegram sign-in could not be verified."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_json = verified.get("user", "")
        try:
            telegram_user_id = json.loads(user_json).get("id") if user_json else None
        except (ValueError, AttributeError):
            telegram_user_id = None
        if telegram_user_id is None:
            return Response(
                {"detail": "Telegram sign-in payload was missing a user id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        link = TelegramLink.objects.filter(
            telegram_user_id=telegram_user_id, unlinked_at__isnull=True
        ).select_related("user").first()
        if link is None:
            return Response(
                {"detail": "Link your Telegram account in UniWay first, then reopen the Mini App."},
                status=status.HTTP_404_NOT_FOUND,
            )

        tokens = token_pair_for_user(link.user)
        response = Response({"access": tokens["access"], "user": CurrentUserSerializer(link.user).data})
        set_refresh_cookie(response, tokens["refresh"])
        return response

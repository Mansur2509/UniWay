import hashlib
import hmac
import time

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from services.telegram_service.models import TelegramLink
from services.telegram_service.services import (
    LinkTokenError,
    consume_link_token,
    is_telegram_configured,
    issue_link_token,
    verify_mini_app_init_data,
)

User = get_user_model()
STRONG_PASSWORD = "Strong-Development-Password-842!"


class TelegramNotConfiguredTests(APITestCase):
    """With no TELEGRAM_BOT_TOKEN set (the default), every endpoint must
    degrade to a clear 503 rather than attempting a live call or crashing."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com", email="student@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(self.user)

    def test_is_telegram_configured_is_false_by_default(self):
        self.assertFalse(is_telegram_configured())

    def test_link_token_endpoint_returns_503_when_unconfigured(self):
        response = self.client.post("/api/v1/telegram/link-token/")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(response.data["telegram_configured"])

    def test_webhook_returns_503_when_unconfigured(self):
        response = self.client.post("/api/v1/telegram/webhook/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_mini_app_session_returns_503_when_unconfigured(self):
        response = self.client.post(
            "/api/v1/telegram/mini-app/session/", {"init_data": "whatever"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


@override_settings(TELEGRAM_BOT_TOKEN="test-bot-token-not-real")
class TelegramLinkFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student2@example.com", email="student2@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(self.user)

    def test_issuing_a_link_token_returns_201_with_token_and_expiry(self):
        response = self.client.post("/api/v1/telegram/link-token/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIn("token", response.data)
        self.assertIn("expires_at", response.data)

    def test_link_status_reports_not_linked_before_linking(self):
        response = self.client.get("/api/v1/telegram/link/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_linked"])

    def test_consuming_a_valid_token_links_the_account(self):
        link_token = issue_link_token(self.user)

        link = consume_link_token(
            token=link_token.token, telegram_user_id=123456789, telegram_username="realstudent"
        )

        self.assertEqual(link.user, self.user)
        self.assertEqual(link.telegram_user_id, 123456789)
        response = self.client.get("/api/v1/telegram/link/")
        self.assertTrue(response.data["is_linked"])
        self.assertEqual(response.data["telegram_username"], "realstudent")

    def test_consuming_an_expired_or_unknown_token_raises(self):
        with self.assertRaises(LinkTokenError):
            consume_link_token(token="not-a-real-token", telegram_user_id=1)

    def test_a_token_cannot_be_consumed_twice(self):
        link_token = issue_link_token(self.user)
        consume_link_token(token=link_token.token, telegram_user_id=1)

        with self.assertRaises(LinkTokenError):
            consume_link_token(token=link_token.token, telegram_user_id=2)

    def test_issuing_a_new_token_invalidates_the_previous_one(self):
        first = issue_link_token(self.user)
        issue_link_token(self.user)

        with self.assertRaises(LinkTokenError):
            consume_link_token(token=first.token, telegram_user_id=1)

    def test_same_telegram_account_cannot_link_two_uniway_accounts(self):
        other_user = User.objects.create_user(
            username="other@example.com", email="other@example.com", password=STRONG_PASSWORD
        )
        consume_link_token(token=issue_link_token(self.user).token, telegram_user_id=999)

        with self.assertRaises(LinkTokenError):
            consume_link_token(token=issue_link_token(other_user).token, telegram_user_id=999)

    def test_unlinking_clears_link_status_but_preserves_the_row(self):
        link_token = issue_link_token(self.user)
        consume_link_token(token=link_token.token, telegram_user_id=1)

        response = self.client.delete("/api/v1/telegram/link/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        status_response = self.client.get("/api/v1/telegram/link/")
        self.assertFalse(status_response.data["is_linked"])
        self.assertTrue(TelegramLink.objects.filter(user=self.user).exists())

    def test_webhook_rejects_wrong_secret_token(self):
        response = self.client.post(
            "/api/v1/telegram/webhook/",
            {"message": {"text": "abc", "from": {"id": 1}}},
            format="json",
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="wrong-secret",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_webhook_with_correct_secret_and_valid_token_links_account(self):
        link_token = issue_link_token(self.user)

        response = self.client.post(
            "/api/v1/telegram/webhook/",
            {"message": {"text": link_token.token, "from": {"id": 555, "username": "webhookuser"}}},
            format="json",
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="test-bot-token-not-real",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(TelegramLink.objects.filter(user=self.user, telegram_user_id=555).exists())

    def test_webhook_never_prints_bot_token_or_link_token_in_response(self):
        link_token = issue_link_token(self.user)
        response = self.client.post(
            "/api/v1/telegram/webhook/",
            {"message": {"text": link_token.token, "from": {"id": 777}}},
            format="json",
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="test-bot-token-not-real",
        )
        self.assertNotIn("test-bot-token-not-real", str(response.data))
        self.assertNotIn(link_token.token, str(response.data))


def _build_signed_init_data(bot_token: str, auth_date: int, user_id: int = 42) -> str:
    fields = {
        "user": f'{{"id":{user_id},"first_name":"Test"}}',
        "auth_date": str(auth_date),
        "query_id": "AAsomequeryid",
    }
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    from urllib.parse import urlencode

    fields["hash"] = computed_hash
    return urlencode(fields)


@override_settings(TELEGRAM_BOT_TOKEN="test-bot-token-not-real")
class MiniAppInitDataVerificationTests(APITestCase):
    def test_correctly_signed_recent_init_data_is_accepted(self):
        init_data = _build_signed_init_data("test-bot-token-not-real", int(time.time()))

        result = verify_mini_app_init_data(init_data)

        self.assertIsNotNone(result)
        self.assertEqual(result["auth_date"], str(result["auth_date"]))

    def test_tampered_init_data_is_rejected(self):
        init_data = _build_signed_init_data("test-bot-token-not-real", int(time.time()))
        tampered = init_data.replace("Test", "Hacker")

        result = verify_mini_app_init_data(tampered)

        self.assertIsNone(result)

    def test_stale_init_data_is_rejected(self):
        old_timestamp = int(time.time()) - 10_000
        init_data = _build_signed_init_data("test-bot-token-not-real", old_timestamp)

        result = verify_mini_app_init_data(init_data)

        self.assertIsNone(result)

    def test_signed_with_wrong_bot_token_is_rejected(self):
        init_data = _build_signed_init_data("a-completely-different-token", int(time.time()))

        result = verify_mini_app_init_data(init_data)

        self.assertIsNone(result)

    def test_mini_app_session_endpoint_issues_session_for_linked_account(self):
        user = User.objects.create_user(
            username="miniapp@example.com", email="miniapp@example.com", password=STRONG_PASSWORD
        )
        link_token = issue_link_token(user)
        consume_link_token(token=link_token.token, telegram_user_id=42)
        init_data = _build_signed_init_data("test-bot-token-not-real", int(time.time()), user_id=42)

        response = self.client.post(
            "/api/v1/telegram/mini-app/session/", {"init_data": init_data}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["email"], "miniapp@example.com")

    def test_mini_app_session_rejects_unlinked_telegram_user(self):
        init_data = _build_signed_init_data("test-bot-token-not-real", int(time.time()), user_id=99999)

        response = self.client.post(
            "/api/v1/telegram/mini-app/session/", {"init_data": init_data}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

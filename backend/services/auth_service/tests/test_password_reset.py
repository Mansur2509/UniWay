from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework.throttling import ScopedRateThrottle

from services.auth_service.models import PasswordResetToken
from services.auth_service.password_reset import _digest

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetApiTests(APITestCase):
    def setUp(self):
        cache.clear()
        mail.outbox = []
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Old-Strong-Password-842!",
        )

    def request_reset(self, email):
        return self.client.post(
            reverse("auth:password-reset-request"), {"email": email}, format="json"
        )

    def extract_token(self):
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        token = body.split("token=")[1].split("\n")[0].strip()
        self.assertTrue(token)
        return token

    def test_request_for_existing_active_email_sends_email_with_token(self):
        response = self.request_reset(self.user.email)

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(PasswordResetToken.objects.filter(user=self.user).count(), 1)
        token = self.extract_token()
        record = PasswordResetToken.objects.get(user=self.user)
        self.assertEqual(record.token_digest, _digest(token))

    def test_request_for_unknown_email_returns_identical_neutral_response(self):
        known = self.request_reset(self.user.email)
        mail.outbox = []
        PasswordResetToken.objects.all().delete()

        unknown = self.request_reset("nobody@example.com")

        self.assertEqual(known.status_code, unknown.status_code)
        self.assertEqual(known.data, unknown.data)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(PasswordResetToken.objects.exists())

    def test_request_for_inactive_user_sends_no_email(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.request_reset(self.user.email)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def confirm(self, token, new_password="New-Strong-Password-842!"):
        return self.client.post(
            reverse("auth:password-reset-confirm"),
            {
                "token": token,
                "new_password": new_password,
                "new_password_confirm": new_password,
            },
            format="json",
        )

    def test_confirm_with_valid_token_resets_password_and_invalidates_token(self):
        self.request_reset(self.user.email)
        token = self.extract_token()

        response = self.confirm(token)

        self.assertEqual(response.status_code, 204, getattr(response, "data", None))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-Strong-Password-842!"))

        replay = self.confirm(token)
        self.assertEqual(replay.status_code, 400)
        self.assertEqual(replay.data.get("code"), ["invalid"])

    def test_confirm_blacklists_outstanding_refresh_tokens(self):
        login = self.client.post(
            reverse("auth:login"),
            {"email": self.user.email, "password": "Old-Strong-Password-842!"},
            format="json",
        )
        old_refresh = login.cookies["uniway_refresh"].value
        self.request_reset(self.user.email)
        token = self.extract_token()

        self.confirm(token)

        refresh_client = APIClient()
        refresh_response = refresh_client.post(
            reverse("auth:token-refresh"), {"refresh": old_refresh}, format="json"
        )
        self.assertEqual(refresh_response.status_code, 401)

    def test_confirm_rejects_mismatched_password_confirmation(self):
        self.request_reset(self.user.email)
        token = self.extract_token()

        response = self.client.post(
            reverse("auth:password-reset-confirm"),
            {
                "token": token,
                "new_password": "New-Strong-Password-842!",
                "new_password_confirm": "Different-Password-842!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old-Strong-Password-842!"))

    def test_confirm_rejects_weak_new_password(self):
        self.request_reset(self.user.email)
        token = self.extract_token()

        response = self.confirm(token, new_password="short")

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old-Strong-Password-842!"))

    def test_confirm_rejects_unknown_token(self):
        response = self.confirm("not-a-real-token")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("code"), ["invalid"])

    def test_confirm_rejects_expired_token(self):
        self.request_reset(self.user.email)
        token = self.extract_token()
        record = PasswordResetToken.objects.get(user=self.user)
        record.expires_at = timezone.now() - timedelta(seconds=1)
        record.save(update_fields=["expires_at"])

        response = self.confirm(token)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("code"), ["expired"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old-Strong-Password-842!"))

    def test_confirm_rejects_token_for_inactive_user(self):
        self.request_reset(self.user.email)
        token = self.extract_token()
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.confirm(token)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("code"), ["invalid"])

    def test_password_reset_request_has_dedicated_rate_limit(self):
        client = APIClient()
        with patch.object(
            ScopedRateThrottle,
            "THROTTLE_RATES",
            {"password_reset_request": "1/minute"},
        ):
            first = client.post(
                reverse("auth:password-reset-request"),
                {"email": self.user.email},
                format="json",
            )
            second = client.post(
                reverse("auth:password-reset-request"),
                {"email": self.user.email},
                format="json",
            )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)

    def test_password_reset_confirm_has_dedicated_rate_limit(self):
        self.request_reset(self.user.email)
        token = self.extract_token()
        client = APIClient()
        with patch.object(
            ScopedRateThrottle,
            "THROTTLE_RATES",
            {"password_reset_confirm": "1/minute"},
        ):
            first = client.post(
                reverse("auth:password-reset-confirm"),
                {
                    "token": "bad-token-one",
                    "new_password": "New-Strong-Password-842!",
                    "new_password_confirm": "New-Strong-Password-842!",
                },
                format="json",
            )
            second = client.post(
                reverse("auth:password-reset-confirm"),
                {
                    "token": token,
                    "new_password": "New-Strong-Password-842!",
                    "new_password_confirm": "New-Strong-Password-842!",
                },
                format="json",
            )

        self.assertEqual(first.status_code, 400)
        self.assertEqual(second.status_code, 429)

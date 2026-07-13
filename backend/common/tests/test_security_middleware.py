from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(ROOT_URLCONF="config.urls")
class PrivateApiCacheControlTests(TestCase):
    def test_auth_response_is_private_and_not_cacheable(self):
        response = self.client.post(
            reverse("auth:login"),
            {"email": "missing@example.com", "password": "invalid-password"},
            content_type="application/json",
        )

        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(response["Pragma"], "no-cache")
        self.assertIn("Authorization", response.get("Vary", ""))
        self.assertIn("Cookie", response.get("Vary", ""))

    def test_public_health_response_is_not_forced_private(self):
        response = self.client.get("/api/v1/health/")

        self.assertNotEqual(response.get("Cache-Control"), "private, no-store")

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from services.subscription_service.models import Plan, Subscription
from services.user_profile_service.models import StudentProfile, UserPreference

User = get_user_model()


class AuthApiTests(APITestCase):
    register_payload = {
        "email": "student@example.com",
        "full_name": "Student Example",
        "password": "Strong-Development-Password-842!",
        "password_confirm": "Strong-Development-Password-842!",
    }

    def register(self):
        return self.client.post(reverse("auth:register"), self.register_payload, format="json")

    def test_register_creates_student_profile_subscription_and_tokens(self):
        response = self.register()

        self.assertEqual(response.status_code, 201, response.json())
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], self.register_payload["email"])
        self.assertEqual(response.data["user"]["role"], User.Role.STUDENT)
        self.assertEqual(response.data["user"]["subscription"]["tier"], Plan.FREE)

        user = User.objects.get(email=self.register_payload["email"])
        self.assertTrue(user.check_password(self.register_payload["password"]))
        self.assertEqual(user.student_profile.full_name, self.register_payload["full_name"])
        self.assertEqual(user.subscription.plan, Plan.FREE)
        self.assertTrue(UserPreference.objects.filter(user=user).exists())

    def test_login_returns_jwt_tokens(self):
        self.register()

        response = self.client.post(
            reverse("auth:login"),
            {
                "email": self.register_payload["email"],
                "password": self.register_payload["password"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.json())
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["full_name"], self.register_payload["full_name"])

    def test_me_requires_authentication_and_returns_related_data(self):
        register_response = self.register()

        anonymous_response = self.client.get(reverse("auth:me"))
        self.assertEqual(anonymous_response.status_code, 401)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {register_response.data['access']}")
        response = self.client.get(reverse("auth:me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["scholarship_need"], "unsure")
        self.assertEqual(response.data["subscription"]["tier"], Plan.FREE)

    def test_me_patch_updates_only_profile_fields(self):
        register_response = self.register()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {register_response.data['access']}")

        response = self.client.patch(
            reverse("auth:me"),
            {
                "full_name": "Updated Student",
                "profile": {
                    "country": "Uzbekistan",
                    "city": "Tashkent",
                    "intended_major": "Computer Science",
                },
                "role": User.Role.ADMIN,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.data["full_name"], "Updated Student")
        self.assertEqual(response.data["profile"]["country"], "Uzbekistan")
        self.assertEqual(response.data["role"], User.Role.STUDENT)

        user = User.objects.get(email=self.register_payload["email"])
        self.assertEqual(user.role, User.Role.STUDENT)

    def test_logout_blacklists_refresh_token(self):
        register_response = self.register()
        access = register_response.data["access"]
        refresh = register_response.data["refresh"]

        logout_response = self.client.post(
            reverse("auth:logout"),
            {"refresh": refresh},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(logout_response.status_code, 204)

        refresh_response = self.client.post(
            reverse("auth:token-refresh"),
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, 401)

    def test_anonymous_logout_is_rejected(self):
        response = self.client.post(
            reverse("auth:logout"),
            {"refresh": "not-a-token"},
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))

    def test_logout_rejects_another_users_refresh_token(self):
        first_user = User.objects.create_user(
            username="first-logout@example.com",
            email="first-logout@example.com",
            password="Strong-Development-Password-842!",
        )
        second_user = User.objects.create_user(
            username="second-logout@example.com",
            email="second-logout@example.com",
            password="Strong-Development-Password-842!",
        )
        first_token = RefreshToken.for_user(first_user)
        second_token = RefreshToken.for_user(second_user)

        response = self.client.post(
            reverse("auth:logout"),
            {"refresh": str(second_token)},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {first_token.access_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_me_repairs_missing_related_records_for_existing_user(self):
        user = User.objects.create_user(
            username="legacy@example.com",
            email="legacy@example.com",
            password="Strong-Development-Password-842!",
        )
        self.client.force_authenticate(user)

        response = self.client.get(reverse("auth:me"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())
        self.assertTrue(Subscription.objects.filter(user=user).exists())

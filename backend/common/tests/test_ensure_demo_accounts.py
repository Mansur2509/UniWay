from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from common.demo_accounts import (
    CANONICAL_STUDENT_DEMO_EMAIL,
    DEMO_PASSWORD,
    LEGACY_STUDENT_DEMO_EMAILS,
    ensure_canonical_student_demo_account,
)

User = get_user_model()


class EnsureCanonicalStudentDemoAccountTests(TestCase):
    def test_creates_canonical_account_when_neither_email_exists(self):
        report = ensure_canonical_student_demo_account(User)

        self.assertEqual(report["action"], "created_new_account")
        user = User.objects.get(email=CANONICAL_STUDENT_DEMO_EMAIL)
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(DEMO_PASSWORD))

    def test_migrates_legacy_account_in_place_preserving_id(self):
        legacy = User.objects.create_user(
            username=LEGACY_STUDENT_DEMO_EMAILS[0],
            email=LEGACY_STUDENT_DEMO_EMAILS[0],
            password="whatever-old-password",
            role=User.Role.STUDENT,
        )
        legacy_pk = legacy.pk

        report = ensure_canonical_student_demo_account(User)

        self.assertEqual(report["action"], "migrated_legacy_account")
        migrated = User.objects.get(pk=legacy_pk)
        self.assertEqual(migrated.email, CANONICAL_STUDENT_DEMO_EMAIL)
        self.assertEqual(migrated.username, CANONICAL_STUDENT_DEMO_EMAIL)
        self.assertTrue(migrated.check_password(DEMO_PASSWORD))
        self.assertFalse(
            User.objects.filter(email__iexact=LEGACY_STUDENT_DEMO_EMAILS[0]).exists()
        )

    def test_second_run_is_idempotent(self):
        ensure_canonical_student_demo_account(User)
        first_count = User.objects.filter(email=CANONICAL_STUDENT_DEMO_EMAIL).count()

        report = ensure_canonical_student_demo_account(User)

        self.assertEqual(report["action"], "already_present")
        self.assertEqual(
            User.objects.filter(email=CANONICAL_STUDENT_DEMO_EMAIL).count(), first_count
        )
        self.assertEqual(User.objects.filter(email=CANONICAL_STUDENT_DEMO_EMAIL).count(), 1)

    def test_collision_deactivates_duplicate_legacy_account_without_deleting_it(self):
        User.objects.create_user(
            username=CANONICAL_STUDENT_DEMO_EMAIL,
            email=CANONICAL_STUDENT_DEMO_EMAIL,
            password=DEMO_PASSWORD,
            role=User.Role.STUDENT,
        )
        legacy = User.objects.create_user(
            username=LEGACY_STUDENT_DEMO_EMAILS[0],
            email=LEGACY_STUDENT_DEMO_EMAILS[0],
            password="whatever-old-password",
            role=User.Role.STUDENT,
        )

        report = ensure_canonical_student_demo_account(User)

        self.assertEqual(report["action"], "already_present")
        self.assertEqual(report["deactivated_duplicates"], [LEGACY_STUDENT_DEMO_EMAILS[0]])
        legacy.refresh_from_db()
        self.assertFalse(legacy.is_active)
        self.assertTrue(User.objects.filter(pk=legacy.pk).exists())

    def test_never_grants_privileged_access_even_if_legacy_account_had_it(self):
        legacy = User.objects.create_user(
            username=LEGACY_STUDENT_DEMO_EMAILS[0],
            email=LEGACY_STUDENT_DEMO_EMAILS[0],
            password="whatever-old-password",
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        ensure_canonical_student_demo_account(User)

        migrated = User.objects.get(pk=legacy.pk)
        self.assertEqual(migrated.role, User.Role.STUDENT)
        self.assertFalse(migrated.is_staff)
        self.assertFalse(migrated.is_superuser)

    def test_command_output_never_prints_password(self):
        out = StringIO()
        call_command("ensure_demo_accounts", stdout=out)

        self.assertNotIn(DEMO_PASSWORD, out.getvalue())
        self.assertIn(CANONICAL_STUDENT_DEMO_EMAIL, out.getvalue())


class EnsureDemoAccountLoginAndAccessTests(APITestCase):
    def setUp(self):
        call_command("ensure_demo_accounts", stdout=StringIO())

    def test_demo_login_succeeds_with_documented_credential(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": CANONICAL_STUDENT_DEMO_EMAIL, "password": DEMO_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_demo_account_cannot_access_admin_moderation_route(self):
        user = User.objects.get(email=CANONICAL_STUDENT_DEMO_EMAIL)
        self.client.force_authenticate(user)

        response = self.client.get("/api/admin/universities/review-queue/")

        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

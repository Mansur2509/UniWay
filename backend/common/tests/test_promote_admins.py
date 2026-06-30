from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class PromoteAdminsCommandTests(APITestCase):
    def setUp(self):
        self.job_detail_url = reverse("university-import:job-detail", kwargs={"pk": 999999})

    def call_promote_admins(self, *emails: str) -> str:
        stdout = StringIO()
        call_command("promote_admins", emails=list(emails), stdout=stdout)
        return stdout.getvalue()

    def test_existing_normal_user_can_be_promoted(self):
        user = User.objects.create_user(
            username="future-admin@example.com",
            email="Future.Admin@Example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )

        output = self.call_promote_admins("future.admin@example.com")

        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("Strong-Development-Password-842!"))
        self.assertIn("promoted:", output)
        # Django normalizes the email domain to lowercase on save; the command
        # reports the actual stored address.
        self.assertIn(f"- {user.email}", output)

    def test_command_is_idempotent(self):
        user = User.objects.create_user(
            username="idempotent-admin@example.com",
            email="idempotent-admin@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )

        first_output = self.call_promote_admins("IDEMPOTENT-ADMIN@example.com")
        second_output = self.call_promote_admins("idempotent-admin@example.com")

        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)
        self.assertIn("promoted:", first_output)
        self.assertIn("- idempotent-admin@example.com", first_output)
        self.assertIn("already_admin:", second_output)
        self.assertIn("- idempotent-admin@example.com", second_output)

    def test_missing_email_is_reported_without_crashing(self):
        output = self.call_promote_admins("missing-admin@example.com")

        self.assertIn("missing_users:", output)
        self.assertIn("- missing-admin@example.com", output)
        self.assertFalse(User.objects.filter(email__iexact="missing-admin@example.com").exists())

    def test_seed_demo_promotes_registered_known_admin(self):
        from common.management.commands.seed_demo import KNOWN_ADMIN_EMAILS

        email = KNOWN_ADMIN_EMAILS[0]
        user = User.objects.create_user(
            username=email,
            email=email,
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )

        call_command("seed_demo", stdout=StringIO())

        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)
        # The deploy-time hook must not have created the other operators yet.
        self.assertFalse(
            User.objects.filter(email__iexact=KNOWN_ADMIN_EMAILS[1]).exists()
        )

    def test_promoted_user_can_access_admin_import_endpoint(self):
        user = User.objects.create_user(
            username="import-admin@example.com",
            email="import-admin@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )
        self.call_promote_admins("import-admin@example.com")
        user.refresh_from_db()

        self.client.force_authenticate(user)
        response = self.client.get(self.job_detail_url)

        self.assertEqual(response.status_code, 404)

    def test_student_and_organizer_still_blocked_from_admin_import_endpoint(self):
        student = User.objects.create_user(
            username="blocked-student@example.com",
            email="blocked-student@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )
        organizer = User.objects.create_user(
            username="blocked-organizer@example.com",
            email="blocked-organizer@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ORGANIZER,
        )

        for user in (student, organizer):
            with self.subTest(role=user.role):
                self.client.force_authenticate(user)
                response = self.client.get(self.job_detail_url)
                self.assertEqual(response.status_code, 403)

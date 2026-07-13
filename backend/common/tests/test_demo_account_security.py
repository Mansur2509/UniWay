from io import StringIO

from django.contrib.auth import get_user_model
from django.test import TestCase

from common.management.commands.seed_demo import Command

User = get_user_model()


class DemoAccountSecurityTests(TestCase):
    def test_seed_keeps_only_student_demo_login_active(self):
        command = Command(stdout=StringIO())
        command.seed_demo_accounts()

        student = User.objects.get(email="student.demo@uniway.local")
        organizer = User.objects.get(email="organizer.demo@uniway.local")
        admin = User.objects.get(email="admin.demo@uniway.local")

        self.assertTrue(student.is_active)
        self.assertTrue(student.has_usable_password())
        for user in (organizer, admin):
            self.assertFalse(user.is_active)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)
            self.assertFalse(user.has_usable_password())

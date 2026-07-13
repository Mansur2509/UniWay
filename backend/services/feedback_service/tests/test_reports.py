from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.throttling import ScopedRateThrottle

from services.feedback_service.models import UserReport

User = get_user_model()

CREATE_URL = "/api/reports/"
LIST_URL = "/api/admin/reports/"


def detail_url(pk: int) -> str:
    return f"/api/admin/reports/{pk}/"


class UserReportSubmissionTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.student = User.objects.create_user(
            username="reporter@example.com",
            email="reporter@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )

    def test_anonymous_user_cannot_submit_report(self):
        response = self.client.post(
            CREATE_URL,
            {"target_type": "university", "target_id": 1, "reason": "Wrong deadline listed."},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_submit_report(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            CREATE_URL,
            {"target_type": "university", "target_id": 42, "reason": "Wrong deadline listed."},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        report = UserReport.objects.get()
        self.assertEqual(report.reporter, self.student)
        self.assertEqual(report.status, UserReport.Status.OPEN)
        self.assertEqual(report.target_id, 42)

    def test_blank_reason_is_rejected(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            CREATE_URL, {"target_type": "event", "target_id": 1, "reason": "   "}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(UserReport.objects.exists())

    def test_client_cannot_set_status_on_create(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            CREATE_URL,
            {
                "target_type": "organizer",
                "target_id": 7,
                "reason": "Suspicious event listings.",
                "status": "resolved",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        report = UserReport.objects.get()
        self.assertEqual(report.status, UserReport.Status.OPEN)

    def test_user_report_submission_is_rate_limited(self):
        self.client.force_authenticate(self.student)
        with patch.object(
            ScopedRateThrottle,
            "THROTTLE_RATES",
            {"report_submit": "2/minute"},
        ):
            first = self.client.post(
                CREATE_URL,
                {"target_type": "event", "target_id": 1, "reason": "First report"},
            )
            second = self.client.post(
                CREATE_URL,
                {"target_type": "event", "target_id": 2, "reason": "Second report"},
            )
            third = self.client.post(
                CREATE_URL,
                {"target_type": "event", "target_id": 3, "reason": "Third report"},
            )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(third.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class UserReportAdminPermissionTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )
        self.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ADMIN,
        )
        self.report = UserReport.objects.create(
            reporter=self.student,
            target_type=UserReport.TargetType.UNIVERSITY,
            target_id=1,
            reason="Outdated tuition figures.",
        )

    def test_anonymous_cannot_list(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_cannot_list(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(results), 1)

    def test_admin_can_filter_by_target_type(self):
        UserReport.objects.create(
            reporter=self.student,
            target_type=UserReport.TargetType.EVENT,
            target_id=2,
            reason="Duplicate listing.",
        )
        self.client.force_authenticate(self.admin)
        response = self.client.get(LIST_URL, {"target_type": "event"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["target_type"], "event")

    def test_student_cannot_update(self):
        self.client.force_authenticate(self.student)
        response = self.client.patch(detail_url(self.report.id), {"status": "resolved"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_resolving_sets_resolved_at(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(detail_url(self.report.id), {"status": "resolved"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, UserReport.Status.RESOLVED)
        self.assertIsNotNone(self.report.resolved_at)

    def test_admin_moving_to_reviewing_does_not_set_resolved_at(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(detail_url(self.report.id), {"status": "reviewing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, UserReport.Status.REVIEWING)
        self.assertIsNone(self.report.resolved_at)

    def test_admin_cannot_edit_reason_via_update(self):
        self.client.force_authenticate(self.admin)
        original_reason = self.report.reason
        response = self.client.patch(detail_url(self.report.id), {"reason": "Rewritten"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.report.refresh_from_db()
        self.assertEqual(self.report.reason, original_reason)

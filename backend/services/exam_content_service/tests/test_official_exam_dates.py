from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from services.exam_content_service.models import OfficialExamDate

User = get_user_model()


class OfficialExamDateApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="exam-user", email="exam-user@test.com", password="testpass123"
        )

    def test_exam_dates_require_authentication(self):
        response = self.client.get("/api/v1/exam-dates/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sat_2026_seed_dates_serialize_with_late_deadlines(self):
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/v1/exam-dates/", {"exam_type": "SAT", "page_size": 20})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertGreaterEqual(len(results), 8)
        march = next(item for item in results if item["name"] == "March SAT 2026")
        self.assertEqual(march["test_date"], "2026-03-14")
        self.assertEqual(march["registration_deadline"], "2026-02-27")
        self.assertEqual(march["late_registration_deadline"], "2026-03-03")
        self.assertEqual(march["verification_status"], "partial")
        self.assertIn("collegeboard.org", march["source_url"])

    def test_ap_subject_and_late_testing_dates_serialize(self):
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/v1/exam-dates/", {"exam_type": "AP", "page_size": 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        calculus = next(
            item for item in response.data["results"] if item["name"] == "AP Calculus BC"
        )
        self.assertEqual(calculus["event_kind"], OfficialExamDate.EventKind.EXAM)
        self.assertEqual(calculus["test_date"], "2026-05-11")
        self.assertEqual(calculus["test_time"], "8 a.m. local time")
        self.assertEqual(calculus["late_test_date"], "2026-05-21")
        self.assertEqual(calculus["late_test_time"], "12 p.m. local time")
        self.assertIn("Uzbekistan", calculus["notes"])

    def test_ap_performance_and_portfolio_deadlines_serialize(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            "/api/v1/exam-dates/",
            {"exam_type": "AP", "event_kind": "performance_task", "page_size": 20},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {item["name"] for item in response.data["results"]}
        self.assertIn("AP Seminar performance tasks", names)
        self.assertIn("AP Computer Science Principles Create task", names)

        portfolio = self.client.get(
            "/api/v1/exam-dates/",
            {"exam_type": "AP", "event_kind": "portfolio_deadline", "page_size": 20},
        )
        self.assertEqual(portfolio.status_code, status.HTTP_200_OK)
        self.assertEqual(portfolio.data["results"][0]["test_date"], "2026-05-08")

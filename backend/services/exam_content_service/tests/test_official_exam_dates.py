from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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

        response = self.client.get(
            "/api/v1/exam-dates/",
            {"exam_type": "SAT", "page_size": 20, "include_past": "true"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertGreaterEqual(len(results), 8)
        march = next(item for item in results if item["name"] == "March SAT 2026")
        self.assertEqual(march["test_date"], "2026-03-14")
        self.assertEqual(march["registration_deadline"], "2026-02-27")
        self.assertEqual(march["late_registration_deadline"], "2026-03-03")
        self.assertEqual(march["verification_status"], "partial")
        self.assertEqual(march["date_status"], "outdated")
        self.assertEqual(march["exam_year"], 2026)
        self.assertIn("collegeboard.org", march["source_url"])

    def test_ap_subject_and_late_testing_dates_serialize(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(
            "/api/v1/exam-dates/",
            {"exam_type": "AP", "page_size": 100, "include_past": "true"},
        )

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
            {
                "exam_type": "AP",
                "event_kind": "performance_task",
                "page_size": 20,
                "include_past": "true",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {item["name"] for item in response.data["results"]}
        self.assertIn("AP Seminar performance tasks", names)
        self.assertIn("AP Computer Science Principles Create task", names)

        portfolio = self.client.get(
            "/api/v1/exam-dates/",
            {
                "exam_type": "AP",
                "event_kind": "portfolio_deadline",
                "page_size": 20,
                "include_past": "true",
            },
        )
        self.assertEqual(portfolio.status_code, status.HTTP_200_OK)
        self.assertEqual(portfolio.data["results"][0]["test_date"], "2026-05-08")

    def test_default_list_excludes_past_dates_but_keeps_unpublished_future_year(self):
        self.client.force_authenticate(self.user)
        OfficialExamDate.objects.create(
            exam_type=OfficialExamDate.ExamType.AP,
            name="AP future verified example",
            test_date=date.today() + timedelta(days=30),
            exam_year=(date.today() + timedelta(days=30)).year,
            academic_year="future",
            source_url="https://apstudents.collegeboard.org/exam-dates",
            source_title="College Board AP Exam Dates",
            last_verified_date=date.today(),
            verification_status=OfficialExamDate.VerificationStatus.VERIFIED,
            local_timezone="local testing time",
        )
        OfficialExamDate.objects.create(
            exam_type=OfficialExamDate.ExamType.AP,
            name="Upcoming AP schedule",
            test_date=None,
            exam_year=date.today().year + 1,
            academic_year=f"{date.today().year}-{date.today().year + 1}",
            source_url="https://apstudents.collegeboard.org/calendar",
            source_title="AP Calendar",
            last_verified_date=date.today(),
            verification_status=OfficialExamDate.VerificationStatus.NOT_PUBLISHED,
        )

        response = self.client.get("/api/v1/exam-dates/", {"exam_type": "AP", "page_size": 200})

        names = {item["name"] for item in response.data["results"]}
        self.assertIn("AP future verified example", names)
        self.assertIn("Upcoming AP schedule", names)
        self.assertNotIn("AP Calculus BC", names)
        unpublished = next(
            item for item in response.data["results"] if item["name"] == "Upcoming AP schedule"
        )
        self.assertIsNone(unpublished["test_date"])
        self.assertEqual(unpublished["date_status"], "not_published")
        self.assertIsNone(unpublished["countdown_days"])

    def test_exam_year_filter_isolated(self):
        self.client.force_authenticate(self.user)
        target_year = date.today().year + 2
        OfficialExamDate.objects.create(
            exam_type=OfficialExamDate.ExamType.AP,
            name="Future AP schedule version",
            test_date=None,
            exam_year=target_year,
            academic_year=str(target_year),
            source_url="https://apstudents.collegeboard.org/calendar",
            last_verified_date=date.today(),
            verification_status=OfficialExamDate.VerificationStatus.NOT_PUBLISHED,
        )

        response = self.client.get(
            "/api/v1/exam-dates/", {"exam_type": "AP", "exam_year": target_year}
        )

        self.assertEqual([item["name"] for item in response.data["results"]], ["Future AP schedule version"])

    def test_unofficial_source_and_mismatched_year_are_rejected(self):
        unofficial = OfficialExamDate(
            exam_type=OfficialExamDate.ExamType.AP,
            name="Unsafe AP source",
            test_date=date.today() + timedelta(days=30),
            exam_year=(date.today() + timedelta(days=30)).year,
            academic_year="future",
            source_url="https://example.com/ap-dates",
            last_verified_date=date.today(),
            verification_status=OfficialExamDate.VerificationStatus.VERIFIED,
        )
        with self.assertRaises(ValidationError):
            unofficial.full_clean()

        mismatch = OfficialExamDate(
            exam_type=OfficialExamDate.ExamType.AP,
            name="Mismatched AP year",
            test_date=date.today() + timedelta(days=30),
            exam_year=date.today().year + 5,
            academic_year="future",
            source_url="https://apstudents.collegeboard.org/calendar",
            last_verified_date=date.today(),
            verification_status=OfficialExamDate.VerificationStatus.VERIFIED,
        )
        with self.assertRaises(ValidationError):
            mismatch.full_clean()

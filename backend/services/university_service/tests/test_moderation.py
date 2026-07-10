from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from services.university_service.models import University, UniversityModerationRecord

User = get_user_model()

QUEUE_URL = "/api/admin/universities/review-queue/"


def moderation_url(university_id: int) -> str:
    return f"/api/admin/universities/{university_id}/moderation/"


def create_university(slug: str, **overrides) -> University:
    defaults = {
        "name": slug.replace("-", " ").title(),
        "country": "Demoland",
        "city": "Sample City",
        "official_website": f"https://example.com/{slug}",
        "is_published": True,
    }
    defaults.update(overrides)
    return University.objects.create(slug=slug, **defaults)


class UniversityModerationApiTests(APITestCase):
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
        self.university = create_university("review-university")

    def test_anonymous_cannot_access_review_queue(self):
        response = self.client.get(QUEUE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_cannot_access_review_queue(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(QUEUE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_flag_moderation_action(self):
        self.client.force_authenticate(self.student)
        response = self.client.patch(
            moderation_url(self.university.id),
            {"status": "pending_review", "issue_type": "user_report"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_flag_creates_moderation_record(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            moderation_url(self.university.id),
            {
                "status": "pending_review",
                "issue_type": "outdated_data",
                "description": "Tuition figures look stale.",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        record = UniversityModerationRecord.objects.get()
        self.assertEqual(record.university, self.university)
        self.assertEqual(record.created_by, self.admin)
        self.assertIsNone(record.resolved_by)
        self.assertIsNone(record.resolved_at)

    def test_verifying_sets_resolved_by_and_resolved_at(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            moderation_url(self.university.id),
            {"status": "verified", "issue_type": "admin_note", "description": "Looks correct."},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        record = UniversityModerationRecord.objects.get()
        self.assertEqual(record.resolved_by, self.admin)
        self.assertIsNotNone(record.resolved_at)

    def test_review_queue_shows_only_open_universities(self):
        other_university = create_university("other-university")
        self.client.force_authenticate(self.admin)
        self.client.patch(
            moderation_url(self.university.id),
            {"status": "pending_review", "issue_type": "missing_source"},
        )
        self.client.patch(
            moderation_url(other_university.id),
            {"status": "verified", "issue_type": "admin_note"},
        )
        response = self.client.get(QUEUE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        university_ids = {row["university"] for row in response.data}
        self.assertIn(self.university.id, university_ids)
        self.assertNotIn(other_university.id, university_ids)

    def test_review_queue_shows_one_row_per_university(self):
        self.client.force_authenticate(self.admin)
        self.client.patch(
            moderation_url(self.university.id),
            {"status": "pending_review", "issue_type": "missing_source"},
        )
        self.client.patch(
            moderation_url(self.university.id),
            {"status": "needs_update", "issue_type": "conflicting_data"},
        )
        response = self.client.get(QUEUE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        matching = [row for row in response.data if row["university"] == self.university.id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["issue_type"], "conflicting_data")

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from services.event_service.models import EventCategory, OrganizerModeration

User = get_user_model()

LIST_URL = "/api/admin/organizers/"


def moderation_url(user_id: int) -> str:
    return f"/api/admin/organizers/{user_id}/moderation/"


class OrganizerModerationApiTests(APITestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer@example.com",
            email="organizer@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ORGANIZER,
        )
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

    def test_anonymous_cannot_list_organizers(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organizer_cannot_list_organizers(self):
        self.client.force_authenticate(self.organizer)
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_organizers(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [row["email"] for row in response.data["results"]]
        self.assertIn(self.organizer.email, emails)
        self.assertNotIn(self.student.email, emails)

    def test_unreviewed_organizer_shows_pending_status(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(LIST_URL)
        row = next(
            row
            for row in response.data["results"]
            if row["email"] == self.organizer.email
        )
        self.assertEqual(row["moderation_status"], "pending")

    def test_student_cannot_moderate_organizer(self):
        self.client.force_authenticate(self.student)
        response = self.client.patch(
            moderation_url(self.organizer.id), {"status": "approved"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_approve_organizer(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            moderation_url(self.organizer.id), {"status": "approved"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        record = OrganizerModeration.objects.get(organizer=self.organizer)
        self.assertEqual(record.status, OrganizerModeration.Status.APPROVED)
        self.assertEqual(record.reviewed_by, self.admin)
        self.assertIsNotNone(record.reviewed_at)


class OrganizerSuspensionEnforcementTests(APITestCase):
    """Confirms IsOrganizerOrAdmin actually blocks a suspended organizer."""

    def setUp(self):
        self.category = EventCategory.objects.create(name="Workshop", slug="workshop")
        self.organizer = User.objects.create_user(
            username="organizer@example.com",
            email="organizer@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ORGANIZER,
        )
        self.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ADMIN,
        )

    def _create_event_payload(self):
        return {
            "title": "Sample Workshop",
            "description": "A workshop for testing.",
            "category_slug": self.category.slug,
            "organizer_name": "Test Organizer",
            "format": "offline",
            "start_at": "2027-01-10T10:00:00Z",
            "location": {"city": "Remote", "country": "Online"},
            "source": {"source_title": "Organizer", "source_url": "https://example.com"},
        }

    def test_organizer_with_no_moderation_record_can_create_event(self):
        self.client.force_authenticate(self.organizer)
        response = self.client.post(
            "/api/organizer/events/", self._create_event_payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_suspended_organizer_cannot_create_event(self):
        OrganizerModeration.objects.create(
            organizer=self.organizer,
            status=OrganizerModeration.Status.SUSPENDED,
            reason="Repeated policy violations.",
        )
        self.client.force_authenticate(self.organizer)
        response = self.client.post(
            "/api/organizer/events/", self._create_event_payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reapproving_a_suspended_organizer_restores_access(self):
        self.client.force_authenticate(self.admin)
        self.client.patch(
            f"/api/admin/organizers/{self.organizer.id}/moderation/",
            {"status": "suspended"},
        )
        self.client.patch(
            f"/api/admin/organizers/{self.organizer.id}/moderation/",
            {"status": "approved"},
        )
        self.client.force_authenticate(self.organizer)
        response = self.client.post(
            "/api/organizer/events/", self._create_event_payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

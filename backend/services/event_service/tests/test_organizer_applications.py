from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from services.activity_service.models import AnalyticsEvent
from services.event_service.models import OrganizerApplication

User = get_user_model()

CREATE_URL = "/api/organizer-applications/"
MINE_URL = "/api/organizer-applications/mine/"


def valid_payload(**overrides):
    payload = {
        "first_name": "Amina",
        "last_name": "Karimova",
        "email": "amina@example.com",
        "telegram_username": "@amina_k",
        "description": "I run a student debate club and want to organize campus events.",
        "project_link": "https://example.com/debate-club",
        "motivation": "I want to bring more academic events to my school.",
        "experience": "Organized 3 debate tournaments last year.",
    }
    payload.update(overrides)
    return payload


class OrganizerApplicationCreateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
        )

    def test_anonymous_cannot_submit(self):
        response = self.client.post(CREATE_URL, valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_student_can_submit(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(CREATE_URL, valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        application = OrganizerApplication.objects.get(applicant=self.user)
        self.assertEqual(application.status, OrganizerApplication.Status.PENDING)
        self.assertEqual(application.telegram_username, "amina_k")

    def test_submission_creates_analytics_event(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(CREATE_URL, valid_payload(), format="json")

        event = AnalyticsEvent.objects.get(
            user=self.user, event_type=AnalyticsEvent.EventType.ORGANIZER_APPLICATION_SUBMITTED
        )
        self.assertEqual(event.entity_id, response.data["id"])

    def test_missing_telegram_username_is_rejected(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(CREATE_URL, valid_payload(telegram_username=""), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_motivation_is_rejected(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(CREATE_URL, valid_payload(motivation=""), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_project_link_is_rejected(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            CREATE_URL, valid_payload(project_link="not-a-url"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_project_link_is_optional(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(CREATE_URL, valid_payload(project_link=""), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_second_submission_while_pending_is_rejected(self):
        self.client.force_authenticate(self.user)
        self.client.post(CREATE_URL, valid_payload(), format="json")

        response = self.client.post(CREATE_URL, valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(OrganizerApplication.objects.filter(applicant=self.user).count(), 1)

    def test_can_reapply_after_previous_application_was_rejected(self):
        OrganizerApplication.objects.create(
            applicant=self.user,
            first_name="Amina",
            last_name="Karimova",
            email="amina@example.com",
            telegram_username="amina_k",
            description="Old application.",
            motivation="Old motivation.",
            status=OrganizerApplication.Status.REJECTED,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.user)

        response = self.client.post(CREATE_URL, valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(OrganizerApplication.objects.filter(applicant=self.user).count(), 2)


class OrganizerApplicationMineTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
        )

    def test_anonymous_cannot_view(self):
        response = self.client.get(MINE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_404_when_no_application_exists(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(MINE_URL)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_most_recent_application_status(self):
        OrganizerApplication.objects.create(
            applicant=self.user,
            first_name="Amina",
            last_name="Karimova",
            email="amina@example.com",
            telegram_username="amina_k",
            description="An application.",
            motivation="A motivation.",
            status=OrganizerApplication.Status.PENDING,
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(MINE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], OrganizerApplication.Status.PENDING)

    def test_does_not_leak_another_users_application(self):
        other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="Strong-Development-Password-842!",
        )
        OrganizerApplication.objects.create(
            applicant=other_user,
            first_name="Other",
            last_name="User",
            email="other@example.com",
            telegram_username="other_user",
            description="An application.",
            motivation="A motivation.",
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(MINE_URL)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

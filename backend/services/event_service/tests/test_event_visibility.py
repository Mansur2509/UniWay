from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from services.event_service.models import Event, EventCategory, EventLocation, EventSource


class EventVisibilityTests(APITestCase):
    def setUp(self):
        category = EventCategory.objects.create(name="Workshop", slug="workshop")
        self.approved = self.create_event(
            category=category,
            slug="approved-event",
            status=Event.Status.PUBLISHED,
        )
        self.pending = self.create_event(
            category=category,
            slug="pending-event",
            status=Event.Status.PENDING_REVIEW,
        )

    def create_event(self, *, category, slug, status):
        event = Event.objects.create(
            category=category,
            title=slug.replace("-", " ").title(),
            slug=slug,
            description="Original demonstration description.",
            organizer_name="Demo organizer",
            format=Event.Format.ONLINE,
            starts_at=timezone.now() + timedelta(days=10),
            deadline=timezone.now() + timedelta(days=5),
            moderation_status=status,
        )
        EventLocation.objects.create(event=event, country="Demo")
        EventSource.objects.create(
            event=event,
            source_title="Demo source",
            source_url=f"https://example.com/{slug}",
            is_official=False,
        )
        return event

    def test_authenticated_list_excludes_pending_events(self):
        user = get_user_model().objects.create_user(
            username="student",
            email="student-list@example.com",
            password="safe-development-password",
        )
        self.client.force_authenticate(user)
        response = self.client.get("/api/events/")

        self.assertEqual(response.status_code, 200)
        slugs = [item["slug"] for item in response.json()["results"]]
        self.assertIn(self.approved.slug, slugs)
        self.assertNotIn(self.pending.slug, slugs)

    def test_anonymous_list_is_rejected(self):
        response = self.client.get("/api/events/")

        self.assertEqual(response.status_code, 401)

    def test_organizer_submission_is_pending_and_keeps_source(self):
        organizer = get_user_model().objects.create_user(
            username="organizer",
            email="organizer@example.com",
            password="safe-development-password",
            role="organizer",
        )
        self.client.force_authenticate(organizer)
        starts_at = timezone.now() + timedelta(days=20)
        response = self.client.post(
            "/api/v1/events/",
            {
                "category": self.approved.category_id,
                "title": "New organizer event",
                "slug": "new-organizer-event",
                "description": "Original organizer submission.",
                "organizer_name": "Example organizer",
                "format": "online",
                "online_url": "https://example.com/new-organizer-event/stream",
                "starts_at": starts_at.isoformat(),
                "deadline": (starts_at - timedelta(days=5)).isoformat(),
                "language": "English",
                "eligibility": "Students",
                "is_free": True,
                "scholarship_available": False,
                "location": {"country": "Demo", "city": "Sample City", "venue": "Online"},
                "source": {
                    "source_title": "Organizer page",
                    "source_url": "https://example.com/new-organizer-event",
                    "is_official": True,
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.json())
        event = Event.objects.get(slug="new-organizer-event")
        self.assertEqual(event.moderation_status, Event.Status.PENDING_REVIEW)
        self.assertEqual(event.organizer, organizer)
        self.assertEqual(event.source.source_url, "https://example.com/new-organizer-event")
        self.assertEqual(event.submission.submitted_by, organizer)

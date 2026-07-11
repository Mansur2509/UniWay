from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from services.event_service.models import (
    Event,
    EventCategory,
    EventLocation,
    EventModerationLog,
    EventRegistration,
    EventSource,
    EventSubmission,
)

User = get_user_model()


class OrganizerWorkflowTests(APITestCase):
    def setUp(self):
        self.category = EventCategory.objects.create(
            name="Workshop",
            slug="workshop",
        )
        self.organizer = User.objects.create_user(
            username="organizer@example.com",
            email="organizer@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ORGANIZER,
        )
        self.other_organizer = User.objects.create_user(
            username="other-organizer@example.com",
            email="other-organizer@example.com",
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

    def event_payload(self, **overrides):
        starts_at = timezone.now() + timedelta(days=20)
        payload = {
            "category_slug": self.category.slug,
            "title": "Organizer Planning Workshop",
            "short_description": "A safe fictional organizer workflow event.",
            "description": "A complete fictional event description for workflow tests.",
            "organizer_name": "Example Academic Organizer",
            "format": Event.Format.OFFLINE,
            "is_online": False,
            "online_url": "",
            "start_at": starts_at.isoformat(),
            "end_at": (starts_at + timedelta(hours=2)).isoformat(),
            "registration_deadline": (starts_at - timedelta(days=5)).isoformat(),
            "capacity": 30,
            "price_type": Event.PriceType.FREE,
            "price_amount": None,
            "currency": "",
            "visibility": Event.Visibility.PUBLIC,
            "cover_image_url": "",
            "language": "English",
            "eligibility": "Students",
            "scholarship_available": False,
            "location": {
                "country": "Uzbekistan",
                "city": "Tashkent",
                "venue": "Example Academic Center",
                "latitude": None,
                "longitude": None,
            },
            "source": {
                "source_title": "Official organizer page",
                "source_url": "https://example.com/organizer-workshop",
                "is_official": True,
            },
        }
        payload.update(overrides)
        return payload

    def create_event_via_api(self):
        self.client.force_authenticate(self.organizer)
        response = self.client.post(
            reverse("organizer-events:list-create"),
            self.event_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return Event.objects.get(pk=response.data["id"])

    def submit_event(self, event):
        self.client.force_authenticate(self.organizer)
        response = self.client.post(
            reverse("organizer-events:submit", kwargs={"slug": event.slug}),
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        event.refresh_from_db()
        return event

    def publish_event(self):
        event = self.submit_event(self.create_event_via_api())
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse("event-moderation:approve", kwargs={"slug": event.slug}),
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        event.refresh_from_db()
        return event

    def test_organizer_creates_draft_that_is_not_public(self):
        event = self.create_event_via_api()

        public_response = self.client.get(
            reverse("events:detail", kwargs={"slug": event.slug})
        )

        self.assertEqual(event.organizer, self.organizer)
        self.assertEqual(event.moderation_status, Event.Status.DRAFT)
        self.assertFalse(EventSubmission.objects.filter(event=event).exists())
        self.assertEqual(public_response.status_code, 404)

    def test_student_cannot_access_organizer_actions(self):
        self.client.force_authenticate(self.student)

        list_response = self.client.get(reverse("organizer-events:list-create"))
        create_response = self.client.post(
            reverse("organizer-events:list-create"),
            self.event_payload(),
            format="json",
        )

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(create_response.status_code, 403)

    def test_organizer_can_edit_own_pending_event_but_not_another_event(self):
        event = self.submit_event(self.create_event_via_api())
        own_url = reverse("organizer-events:detail", kwargs={"slug": event.slug})

        own_response = self.client.patch(
            own_url,
            {"short_description": "Updated while pending review."},
            format="json",
        )
        self.client.force_authenticate(self.other_organizer)
        other_response = self.client.patch(
            own_url,
            {"short_description": "Unauthorized change."},
            format="json",
        )

        self.assertEqual(own_response.status_code, 200, own_response.data)
        self.assertEqual(other_response.status_code, 404)
        event.refresh_from_db()
        self.assertEqual(
            event.short_description,
            "Updated while pending review.",
        )

    def test_submit_creates_submission_and_moderation_log(self):
        event = self.submit_event(self.create_event_via_api())

        self.assertEqual(event.moderation_status, Event.Status.PENDING_REVIEW)
        self.assertEqual(event.submission.submitted_by, self.organizer)
        log = EventModerationLog.objects.get(event=event)
        self.assertEqual(log.previous_status, Event.Status.DRAFT)
        self.assertEqual(log.new_status, Event.Status.PENDING_REVIEW)

    def test_admin_approves_pending_event_and_it_becomes_public(self):
        event = self.publish_event()
        self.client.force_authenticate(self.student)

        public_response = self.client.get(
            reverse("events:detail", kwargs={"slug": event.slug})
        )

        self.assertEqual(event.moderation_status, Event.Status.PUBLISHED)
        self.assertEqual(public_response.status_code, 200)

    def test_admin_rejects_with_reason_and_organizer_can_resubmit(self):
        event = self.submit_event(self.create_event_via_api())
        self.client.force_authenticate(self.admin)
        missing_reason_response = self.client.post(
            reverse("event-moderation:reject", kwargs={"slug": event.slug}),
            {},
            format="json",
        )
        reject_response = self.client.post(
            reverse("event-moderation:reject", kwargs={"slug": event.slug}),
            {"reason": "Please clarify the official source and venue."},
            format="json",
        )

        self.assertEqual(missing_reason_response.status_code, 400)
        self.assertEqual(reject_response.status_code, 200, reject_response.data)
        event.refresh_from_db()
        self.assertEqual(event.moderation_status, Event.Status.REJECTED)
        rejection_log = event.moderation_logs.get(new_status=Event.Status.REJECTED)
        self.assertEqual(
            rejection_log.note,
            "Please clarify the official source and venue.",
        )
        self.assertEqual(
            self.client.get(reverse("events:detail", kwargs={"slug": event.slug})).status_code,
            404,
        )

        self.client.force_authenticate(self.organizer)
        update_response = self.client.patch(
            reverse("organizer-events:detail", kwargs={"slug": event.slug}),
            {"source": {"source_url": "https://example.com/updated-official-source"}},
            format="json",
        )
        resubmit_response = self.client.post(
            reverse("organizer-events:submit", kwargs={"slug": event.slug}),
            format="json",
        )

        self.assertEqual(update_response.status_code, 200, update_response.data)
        self.assertEqual(resubmit_response.status_code, 200, resubmit_response.data)
        event.refresh_from_db()
        self.assertEqual(event.moderation_status, Event.Status.PENDING_REVIEW)

    def test_organizer_sees_privacy_limited_participants_for_own_published_event(self):
        event = self.publish_event()
        EventRegistration.objects.create(
            event=event,
            user=self.student,
            registration_data={"full_name": "Student Example", "country": "Uzbekistan"},
            contact_snapshot={
                "email": "student@example.com",
                "telegram_username": "@student_example",
                "phone": "+998 90 123 45 67",
            },
        )

        self.client.force_authenticate(self.organizer)
        response = self.client.get(
            reverse("organizer-events:registrations", kwargs={"slug": event.slug})
        )

        self.assertEqual(response.status_code, 200, response.data)
        participant = response.data["results"][0]
        self.assertEqual(participant["full_name"], "Student Example")
        self.assertEqual(participant["email"], "student@example.com")
        self.assertEqual(participant["telegram_username"], "@student_example")
        self.assertNotIn("phone", participant)
        self.assertNotIn("registration_data", participant)
        self.assertNotIn("contact_snapshot", participant)

        self.client.force_authenticate(self.other_organizer)
        other_response = self.client.get(
            reverse("organizer-events:registrations", kwargs={"slug": event.slug})
        )
        self.assertEqual(other_response.status_code, 404)

    def test_only_admin_can_read_logs_and_admin_cannot_approve_own_event(self):
        event = self.submit_event(self.create_event_via_api())
        logs_url = reverse("event-moderation:logs", kwargs={"slug": event.slug})

        self.client.force_authenticate(self.organizer)
        organizer_logs_response = self.client.get(logs_url)
        self.client.force_authenticate(self.admin)
        admin_logs_response = self.client.get(logs_url)

        self.assertEqual(organizer_logs_response.status_code, 403)
        self.assertEqual(admin_logs_response.status_code, 200)
        self.assertEqual(len(admin_logs_response.data), 1)

        admin_owned_event = Event.objects.create(
            organizer=self.admin,
            category=self.category,
            title="Admin-owned pending event",
            slug="admin-owned-pending-event",
            description="Fictional pending event.",
            organizer_name="Admin organizer",
            format=Event.Format.OFFLINE,
            starts_at=timezone.now() + timedelta(days=10),
            moderation_status=Event.Status.PENDING_REVIEW,
        )
        EventLocation.objects.create(
            event=admin_owned_event,
            country="Uzbekistan",
        )
        EventSource.objects.create(
            event=admin_owned_event,
            source_title="Admin source",
            source_url="https://example.com/admin-event",
        )
        approve_response = self.client.post(
            reverse(
                "event-moderation:approve",
                kwargs={"slug": admin_owned_event.slug},
            ),
            format="json",
        )
        self.assertEqual(approve_response.status_code, 400)

    def test_organizer_can_cancel_published_and_archive_draft(self):
        published = self.publish_event()
        draft = self.create_event_via_api()
        self.client.force_authenticate(self.organizer)

        cancel_response = self.client.post(
            reverse("organizer-events:cancel", kwargs={"slug": published.slug}),
            format="json",
        )
        archive_response = self.client.post(
            reverse("organizer-events:archive", kwargs={"slug": draft.slug}),
            format="json",
        )

        self.assertEqual(cancel_response.status_code, 200, cancel_response.data)
        self.assertEqual(archive_response.status_code, 200, archive_response.data)
        published.refresh_from_db()
        draft.refresh_from_db()
        self.assertEqual(published.moderation_status, Event.Status.CANCELLED)
        self.assertEqual(draft.moderation_status, Event.Status.ARCHIVED)

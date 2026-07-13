import csv
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from services.event_service.models import (
    Event,
    EventCategory,
    EventFormField,
    EventLocation,
    EventNotification,
    EventRegistration,
    EventSource,
    EventTicket,
    ParticipationRecord,
)

User = get_user_model()


class EventInfrastructureTestCase(APITestCase):
    def setUp(self):
        self.category = EventCategory.objects.create(name="Workshop", slug="workshop")
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
        self.other_student = User.objects.create_user(
            username="other-student@example.com",
            email="other-student@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )
        self.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ADMIN,
        )

    def create_event(self, *, organizer=None, status=Event.Status.PUBLISHED, capacity=10, slug="infra-workshop"):
        starts_at = timezone.now() + timedelta(days=10)
        event = Event.objects.create(
            organizer=organizer or self.organizer,
            category=self.category,
            title=slug.replace("-", " ").title(),
            slug=slug,
            short_description="Fictional infrastructure test event.",
            description="Fictional infrastructure test event description.",
            organizer_name="Demo organizer",
            format=Event.Format.OFFLINE,
            is_online=False,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            deadline=timezone.now() + timedelta(days=5),
            capacity=capacity,
            price_type=Event.PriceType.FREE,
            is_free=True,
            moderation_status=status,
            visibility=Event.Visibility.PUBLIC,
        )
        EventLocation.objects.create(event=event, country="Uzbekistan", city="Tashkent", venue="Demo venue")
        EventSource.objects.create(
            event=event,
            source_title="Demo source",
            source_url=f"https://example.com/{slug}",
            is_official=False,
        )
        return event

    def add_form_fields(self, event, *, fields):
        self.client.force_authenticate(self.organizer)
        response = self.client.put(
            reverse("organizer-events:form", kwargs={"slug": event.slug}),
            {"fields": fields},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        return response.data["fields"]

    def register(self, event, user, *, answers=None):
        self.client.force_authenticate(user)
        payload = {"answers": answers} if answers is not None else {}
        return self.client.post(
            reverse("events:register", kwargs={"slug": event.slug}),
            payload,
            format="json",
        )


class CustomFormFieldTests(EventInfrastructureTestCase):
    def test_organizer_can_define_and_read_own_form(self):
        event = self.create_event(status=Event.Status.DRAFT)

        fields = self.add_form_fields(
            event,
            fields=[
                {"field_type": "short_text", "label": "Motivation", "is_required": True},
                {
                    "field_type": "single_choice",
                    "label": "T-shirt size",
                    "choices": ["S", "M", "L"],
                    "is_required": False,
                },
            ],
        )

        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["label"], "Motivation")
        self.assertEqual(fields[1]["choices"], ["S", "M", "L"])

        get_response = self.client.get(
            reverse("organizer-events:form", kwargs={"slug": event.slug})
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data["fields"]), 2)

    def test_organizer_cannot_manage_another_organizers_form(self):
        event = self.create_event(status=Event.Status.DRAFT)
        self.client.force_authenticate(self.other_organizer)

        response = self.client.put(
            reverse("organizer-events:form", kwargs={"slug": event.slug}),
            {"fields": [{"field_type": "short_text", "label": "Hijack attempt"}]},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(EventFormField.objects.filter(event=event).count(), 0)

    def test_student_cannot_manage_form(self):
        event = self.create_event(status=Event.Status.DRAFT)
        self.client.force_authenticate(self.student)

        response = self.client.put(
            reverse("organizer-events:form", kwargs={"slug": event.slug}),
            {"fields": []},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_too_many_fields_are_rejected(self):
        event = self.create_event(status=Event.Status.DRAFT)
        self.client.force_authenticate(self.organizer)

        payload = [
            {"field_type": "short_text", "label": f"Field {index}"} for index in range(21)
        ]
        response = self.client.put(
            reverse("organizer-events:form", kwargs={"slug": event.slug}),
            {"fields": payload},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_choice_field_requires_at_least_one_choice(self):
        event = self.create_event(status=Event.Status.DRAFT)
        self.client.force_authenticate(self.organizer)

        response = self.client.put(
            reverse("organizer-events:form", kwargs={"slug": event.slug}),
            {"fields": [{"field_type": "single_choice", "label": "Pick one", "choices": []}]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_published_event_form_is_locked(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        self.client.force_authenticate(self.organizer)

        response = self.client.put(
            reverse("organizer-events:form", kwargs={"slug": event.slug}),
            {"fields": [{"field_type": "short_text", "label": "Too late"}]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)


class RegistrationAnswersAndTicketTests(EventInfrastructureTestCase):
    def test_registration_requires_required_custom_fields(self):
        event = self.create_event(status=Event.Status.DRAFT)
        fields = self.add_form_fields(
            event,
            fields=[{"field_type": "short_text", "label": "Motivation", "is_required": True}],
        )
        event.moderation_status = Event.Status.PUBLISHED
        event.save(update_fields=["moderation_status"])
        field_id = str(fields[0]["id"])

        missing_response = self.register(event, self.student)
        filled_response = self.register(event, self.student, answers={field_id: "Because I care."})

        self.assertEqual(missing_response.status_code, 400)
        self.assertEqual(filled_response.status_code, 201, filled_response.data)
        registration = EventRegistration.objects.get(event=event, user=self.student)
        answer = registration.answers.get(field_id=field_id)
        self.assertEqual(answer.value, "Because I care.")

    def test_unknown_answer_key_is_rejected_when_event_has_a_form(self):
        event = self.create_event(status=Event.Status.DRAFT)
        self.add_form_fields(
            event,
            fields=[{"field_type": "short_text", "label": "Motivation", "is_required": False}],
        )
        event.moderation_status = Event.Status.PUBLISHED
        event.save(update_fields=["moderation_status"])

        response = self.register(event, self.student, answers={"999999": "nope"})

        self.assertEqual(response.status_code, 400)

    def test_answers_are_ignored_when_event_has_no_form(self):
        event = self.create_event(status=Event.Status.PUBLISHED)

        response = self.register(event, self.student, answers={"999999": "harmless"})

        self.assertEqual(response.status_code, 201, response.data)

    def test_registration_issues_an_active_ticket(self):
        event = self.create_event(status=Event.Status.PUBLISHED)

        response = self.register(event, self.student)

        self.assertEqual(response.status_code, 201, response.data)
        registration = EventRegistration.objects.get(event=event, user=self.student)
        ticket = EventTicket.objects.get(registration=registration)
        self.assertEqual(ticket.status, EventTicket.Status.ACTIVE)
        self.assertTrue(ticket.code)
        self.assertEqual(response.data["ticket"]["status"], EventTicket.Status.ACTIVE)

    def test_cancel_deactivates_ticket_and_reregister_issues_new_active_ticket(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        self.register(event, self.student)
        registration = EventRegistration.objects.get(event=event, user=self.student)
        first_code = registration.ticket.code
        self.client.force_authenticate(self.student)

        self.client.post(reverse("events:cancel-registration", kwargs={"slug": event.slug}), format="json")
        registration.refresh_from_db()
        cancelled_ticket_status = registration.ticket.status

        self.register(event, self.student)
        registration.refresh_from_db()

        self.assertEqual(cancelled_ticket_status, EventTicket.Status.CANCELLED)
        self.assertEqual(registration.ticket.status, EventTicket.Status.ACTIVE)
        self.assertNotEqual(registration.ticket.code, first_code)


class CheckInTests(EventInfrastructureTestCase):
    def register_and_get_registration(self, event, user):
        self.register(event, user)
        return EventRegistration.objects.get(event=event, user=user)

    def test_organizer_checks_in_participant_and_creates_participation_record(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        registration = self.register_and_get_registration(event, self.student)
        self.client.force_authenticate(self.organizer)

        response = self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": event.slug, "registration_id": registration.id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        registration.refresh_from_db()
        self.assertEqual(registration.status, EventRegistration.Status.ATTENDED)
        self.assertEqual(registration.ticket.status, EventTicket.Status.CHECKED_IN)
        record = ParticipationRecord.objects.get(registration=registration)
        self.assertEqual(record.verification_status, ParticipationRecord.VerificationStatus.VERIFIED)
        self.assertTrue(record.public_verification_code)

    def test_check_in_is_idempotent(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        registration = self.register_and_get_registration(event, self.student)
        self.client.force_authenticate(self.organizer)
        url = reverse(
            "organizer-events:registration-check-in",
            kwargs={"slug": event.slug, "registration_id": registration.id},
        )

        self.client.post(url, format="json")
        first_record = ParticipationRecord.objects.get(registration=registration)
        self.client.post(url, format="json")
        second_record = ParticipationRecord.objects.get(registration=registration)

        self.assertEqual(first_record.record_id, second_record.record_id)
        self.assertEqual(
            first_record.public_verification_code, second_record.public_verification_code
        )
        self.assertEqual(ParticipationRecord.objects.filter(registration=registration).count(), 1)

    def test_cancelled_registration_cannot_be_checked_in(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        registration = self.register_and_get_registration(event, self.student)
        self.client.force_authenticate(self.student)
        self.client.post(reverse("events:cancel-registration", kwargs={"slug": event.slug}), format="json")

        self.client.force_authenticate(self.organizer)
        response = self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": event.slug, "registration_id": registration.id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(ParticipationRecord.objects.filter(registration=registration).exists())

    def test_other_organizer_cannot_check_in_participant(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        registration = self.register_and_get_registration(event, self.student)
        self.client.force_authenticate(self.other_organizer)

        response = self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": event.slug, "registration_id": registration.id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_student_cannot_check_in(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        registration = self.register_and_get_registration(event, self.student)
        self.client.force_authenticate(self.student)

        response = self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": event.slug, "registration_id": registration.id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_ticket_verify_by_code(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        registration = self.register_and_get_registration(event, self.student)
        self.client.force_authenticate(self.organizer)

        valid_response = self.client.post(
            reverse("organizer-events:ticket-verify", kwargs={"slug": event.slug}),
            {"code": registration.ticket.code},
            format="json",
        )
        invalid_response = self.client.post(
            reverse("organizer-events:ticket-verify", kwargs={"slug": event.slug}),
            {"code": "not-a-real-code"},
            format="json",
        )

        self.assertEqual(valid_response.status_code, 200, valid_response.data)
        self.assertEqual(valid_response.data["id"], registration.id)
        self.assertEqual(invalid_response.status_code, 400)


class ExportAndAnalyticsTests(EventInfrastructureTestCase):
    def test_export_contains_participant_and_custom_answers(self):
        event = self.create_event(status=Event.Status.DRAFT)
        fields = self.add_form_fields(
            event,
            fields=[{"field_type": "short_text", "label": "Motivation", "is_required": True}],
        )
        event.moderation_status = Event.Status.PUBLISHED
        event.save(update_fields=["moderation_status"])
        field_id = str(fields[0]["id"])
        self.register(event, self.student, answers={field_id: "Great reason."})

        self.client.force_authenticate(self.organizer)
        response = self.client.get(
            reverse("organizer-events:registrations-export", kwargs={"slug": event.slug})
        )

        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        self.assertIn("Motivation", body)
        self.assertIn("Great reason.", body)
        self.assertIn(self.student.email, body)

    def test_export_neutralizes_spreadsheet_formula_prefixes(self):
        event = self.create_event(status=Event.Status.DRAFT)
        fields = self.add_form_fields(
            event,
            fields=[
                {"field_type": "short_text", "label": "Equals", "is_required": True},
                {"field_type": "short_text", "label": "Plus", "is_required": True},
                {"field_type": "short_text", "label": "Minus", "is_required": True},
                {"field_type": "short_text", "label": "At", "is_required": True},
            ],
        )
        event.moderation_status = Event.Status.PUBLISHED
        event.save(update_fields=["moderation_status"])
        answers = {
            str(fields[0]["id"]): "=1+1",
            str(fields[1]["id"]): "+cmd",
            str(fields[2]["id"]): " -10",
            str(fields[3]["id"]): "@SUM(A1:A2)",
        }
        self.register(event, self.student, answers=answers)
        self.client.force_authenticate(self.organizer)

        response = self.client.get(
            reverse("organizer-events:registrations-export", kwargs={"slug": event.slug})
        )

        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(StringIO(response.content.decode("utf-8"))))
        self.assertEqual(rows[-1][-4:], ["'=1+1", "'+cmd", "'-10", "'@SUM(A1:A2)"])

    def test_export_is_scoped_to_owning_organizer(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        self.register(event, self.student)
        self.client.force_authenticate(self.other_organizer)

        response = self.client.get(
            reverse("organizer-events:registrations-export", kwargs={"slug": event.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_export_requires_published_event(self):
        event = self.create_event(status=Event.Status.DRAFT)
        self.client.force_authenticate(self.organizer)

        response = self.client.get(
            reverse("organizer-events:registrations-export", kwargs={"slug": event.slug})
        )

        self.assertEqual(response.status_code, 400)

    def test_analytics_are_scoped_per_organizer(self):
        published = self.create_event(status=Event.Status.PUBLISHED, slug="analytics-published")
        self.create_event(status=Event.Status.DRAFT, slug="analytics-draft")
        registration = self.register_and_get_registration(published, self.student)
        self.client.force_authenticate(self.organizer)
        self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": published.slug, "registration_id": registration.id},
            ),
            format="json",
        )
        self.create_event(
            organizer=self.other_organizer,
            status=Event.Status.PUBLISHED,
            slug="other-organizer-event",
        )

        response = self.client.get(reverse("organizer-events:analytics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_events"], 2)
        self.assertEqual(response.data["published_count"], 1)
        self.assertEqual(response.data["draft_count"], 1)
        self.assertEqual(response.data["total_registrations"], 1)
        self.assertEqual(response.data["checked_in_count"], 1)
        self.assertEqual(response.data["attendance_rate"], 100.0)

    def register_and_get_registration(self, event, user):
        self.register(event, user)
        return EventRegistration.objects.get(event=event, user=user)


class NotificationAndParticipationRecordTests(EventInfrastructureTestCase):
    def test_registration_notifies_student_and_organizer_only(self):
        event = self.create_event(status=Event.Status.PUBLISHED)

        self.register(event, self.student)

        self.assertTrue(
            EventNotification.objects.filter(
                recipient=self.student,
                notification_type=EventNotification.NotificationType.REGISTRATION_CONFIRMED,
            ).exists()
        )
        self.assertTrue(
            EventNotification.objects.filter(
                recipient=self.organizer,
                notification_type=EventNotification.NotificationType.ORGANIZER_NEW_REGISTRATION,
            ).exists()
        )

        self.client.force_authenticate(self.student)
        student_response = self.client.get(reverse("events:my-notifications"))
        self.client.force_authenticate(self.other_student)
        other_student_response = self.client.get(reverse("events:my-notifications"))

        self.assertEqual(student_response.data["count"], 1)
        self.assertEqual(other_student_response.data["count"], 0)

    def test_checkin_notifies_participation_verified(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        self.register(event, self.student)
        registration = EventRegistration.objects.get(event=event, user=self.student)
        self.client.force_authenticate(self.organizer)
        self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": event.slug, "registration_id": registration.id},
            ),
            format="json",
        )

        self.assertTrue(
            EventNotification.objects.filter(
                recipient=self.student,
                notification_type=EventNotification.NotificationType.PARTICIPATION_VERIFIED,
            ).exists()
        )

    def test_student_sees_only_own_participation_records(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        self.register(event, self.student)
        registration = EventRegistration.objects.get(event=event, user=self.student)
        self.client.force_authenticate(self.organizer)
        self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": event.slug, "registration_id": registration.id},
            ),
            format="json",
        )

        self.client.force_authenticate(self.student)
        own_response = self.client.get(reverse("events:participation-records"))
        self.client.force_authenticate(self.other_student)
        other_response = self.client.get(reverse("events:participation-records"))

        self.assertEqual(own_response.data["count"], 1)
        self.assertEqual(other_response.data["count"], 0)


class AdminAuditAccessTests(EventInfrastructureTestCase):
    def test_admin_can_check_in_for_any_organizers_event(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        self.register(event, self.student)
        registration = EventRegistration.objects.get(event=event, user=self.student)
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse(
                "organizer-events:registration-check-in",
                kwargs={"slug": event.slug, "registration_id": registration.id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)

    def test_admin_can_export_any_organizers_participants(self):
        event = self.create_event(status=Event.Status.PUBLISHED)
        self.register(event, self.student)
        self.client.force_authenticate(self.admin)

        response = self.client.get(
            reverse("organizer-events:registrations-export", kwargs={"slug": event.slug})
        )

        self.assertEqual(response.status_code, 200)

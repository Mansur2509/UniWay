from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers

from services.user_profile_service.services import ensure_profile_records

from .models import (
    Event,
    EventModerationLog,
    EventRegistration,
    EventSubmission,
)

ACTIVE_REGISTRATION_STATUSES = (
    EventRegistration.Status.REGISTERED,
    EventRegistration.Status.WAITLISTED,
    EventRegistration.Status.ATTENDED,
)

ORGANIZER_EDITABLE_STATUSES = (
    Event.Status.DRAFT,
    Event.Status.PENDING_REVIEW,
    Event.Status.REJECTED,
)


def generate_unique_event_slug(title: str) -> str:
    base_slug = slugify(title)[:240] or "event"
    slug = base_slug
    suffix = 2
    while Event.objects.filter(slug=slug).exists():
        slug = f"{base_slug[:240 - len(str(suffix)) - 1]}-{suffix}"
        suffix += 1
    return slug


def validate_event_is_editable(event: Event) -> None:
    if event.moderation_status not in ORGANIZER_EDITABLE_STATUSES:
        raise serializers.ValidationError(
            {"status": "Only draft, pending, or rejected events can be edited."}
        )


def _log_transition(
    *,
    event: Event,
    actor,
    previous_status: str,
    new_status: str,
    note: str = "",
) -> None:
    EventModerationLog.objects.create(
        event=event,
        moderator=actor,
        previous_status=previous_status,
        new_status=new_status,
        note=note,
    )


@transaction.atomic
def submit_event_for_review(*, event: Event, actor) -> Event:
    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    if locked_event.moderation_status not in (
        Event.Status.DRAFT,
        Event.Status.REJECTED,
    ):
        raise serializers.ValidationError(
            {"status": "Only draft or rejected events can be submitted."}
        )

    previous_status = locked_event.moderation_status
    locked_event.moderation_status = Event.Status.PENDING_REVIEW
    locked_event.save(update_fields=["moderation_status", "updated_at"])
    submission, created = EventSubmission.objects.get_or_create(
        event=locked_event,
        defaults={"submitted_by": actor},
    )
    if not created:
        submission.submitted_by = actor
        submission.submitted_at = timezone.now()
        submission.save(update_fields=["submitted_by", "submitted_at"])
    _log_transition(
        event=locked_event,
        actor=actor,
        previous_status=previous_status,
        new_status=Event.Status.PENDING_REVIEW,
        note="Submitted for moderation.",
    )
    return locked_event


@transaction.atomic
def approve_event(*, event: Event, actor) -> Event:
    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    if locked_event.organizer_id == actor.id:
        raise serializers.ValidationError(
            {"event": "Moderators cannot approve their own event."}
        )
    if locked_event.moderation_status != Event.Status.PENDING_REVIEW:
        raise serializers.ValidationError(
            {"status": "Only pending events can be approved."}
        )

    locked_event.moderation_status = Event.Status.PUBLISHED
    locked_event.save(update_fields=["moderation_status", "updated_at"])
    _log_transition(
        event=locked_event,
        actor=actor,
        previous_status=Event.Status.PENDING_REVIEW,
        new_status=Event.Status.PUBLISHED,
        note="Approved for publication.",
    )
    return locked_event


@transaction.atomic
def reject_event(*, event: Event, actor, reason: str) -> Event:
    reason = reason.strip()
    if not reason:
        raise serializers.ValidationError({"reason": "A rejection reason is required."})

    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    if locked_event.organizer_id == actor.id:
        raise serializers.ValidationError(
            {"event": "Moderators cannot reject their own event."}
        )
    if locked_event.moderation_status != Event.Status.PENDING_REVIEW:
        raise serializers.ValidationError(
            {"status": "Only pending events can be rejected."}
        )

    locked_event.moderation_status = Event.Status.REJECTED
    locked_event.save(update_fields=["moderation_status", "updated_at"])
    _log_transition(
        event=locked_event,
        actor=actor,
        previous_status=Event.Status.PENDING_REVIEW,
        new_status=Event.Status.REJECTED,
        note=reason,
    )
    return locked_event


@transaction.atomic
def archive_event(*, event: Event, actor, is_admin: bool = False) -> Event:
    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    allowed_statuses = (
        tuple(Event.Status.values)
        if is_admin
        else (
            Event.Status.DRAFT,
            Event.Status.PENDING_REVIEW,
            Event.Status.REJECTED,
        )
    )
    if locked_event.moderation_status not in allowed_statuses:
        raise serializers.ValidationError(
            {"status": "This event cannot be archived in its current status."}
        )
    if locked_event.moderation_status == Event.Status.ARCHIVED:
        raise serializers.ValidationError({"status": "This event is already archived."})

    previous_status = locked_event.moderation_status
    locked_event.moderation_status = Event.Status.ARCHIVED
    locked_event.save(update_fields=["moderation_status", "updated_at"])
    _log_transition(
        event=locked_event,
        actor=actor,
        previous_status=previous_status,
        new_status=Event.Status.ARCHIVED,
        note="Event archived.",
    )
    return locked_event


@transaction.atomic
def cancel_owned_event(*, event: Event, actor) -> Event:
    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    if locked_event.moderation_status != Event.Status.PUBLISHED:
        raise serializers.ValidationError(
            {"status": "Only published events can be cancelled."}
        )

    locked_event.moderation_status = Event.Status.CANCELLED
    locked_event.save(update_fields=["moderation_status", "updated_at"])
    _log_transition(
        event=locked_event,
        actor=actor,
        previous_status=Event.Status.PUBLISHED,
        new_status=Event.Status.CANCELLED,
        note="Event cancelled by its organizer.",
    )
    return locked_event


def build_registration_snapshots(user) -> tuple[dict, dict]:
    profile, preferences = ensure_profile_records(user)
    registration_data = {
        "full_name": profile.full_name,
        "country": profile.country,
        "city": profile.city,
        "school_or_university": profile.school_or_university,
        "grade": profile.grade,
        "education_status": profile.education_status,
        "intended_degree": profile.intended_degree,
        "intended_majors": profile.intended_majors,
        "interests": preferences.interests,
        "languages": profile.languages,
    }
    contact_snapshot = {
        "email": user.email,
        "telegram_username": profile.telegram_username,
        "phone": profile.phone,
    }
    return registration_data, contact_snapshot


def payment_status_for_event(event: Event) -> str:
    if event.price_type == Event.PriceType.FREE:
        return EventRegistration.PaymentStatus.NOT_REQUIRED
    return EventRegistration.PaymentStatus.PENDING


@transaction.atomic
def register_for_event(*, event: Event, user) -> tuple[EventRegistration, bool]:
    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    now = timezone.now()

    if locked_event.moderation_status != Event.Status.PUBLISHED:
        raise serializers.ValidationError({"event": "This event is not open for registration."})
    if locked_event.visibility != Event.Visibility.PUBLIC:
        raise serializers.ValidationError({"event": "This event is not publicly registerable."})
    if locked_event.deadline and locked_event.deadline < now:
        raise serializers.ValidationError({"event": "The registration deadline has passed."})
    if locked_event.starts_at <= now:
        raise serializers.ValidationError({"event": "Registration is closed because the event has started."})

    active_registration = EventRegistration.objects.filter(
        user=user,
        event=locked_event,
        status__in=ACTIVE_REGISTRATION_STATUSES,
    ).first()
    if active_registration:
        raise serializers.ValidationError({"event": "You are already registered for this event."})

    active_count = EventRegistration.objects.filter(
        event=locked_event,
        status__in=(
            EventRegistration.Status.REGISTERED,
            EventRegistration.Status.ATTENDED,
        ),
    ).count()
    if locked_event.capacity is not None and active_count >= locked_event.capacity:
        raise serializers.ValidationError({"event": "This event has reached capacity."})

    registration_data, contact_snapshot = build_registration_snapshots(user)
    cancelled_registration = (
        EventRegistration.objects.select_for_update()
        .filter(
            user=user,
            event=locked_event,
            status=EventRegistration.Status.CANCELLED,
        )
        .order_by("-updated_at")
        .first()
    )
    defaults = {
        "status": EventRegistration.Status.REGISTERED,
        "registration_data": registration_data,
        "contact_snapshot": contact_snapshot,
        "payment_status": payment_status_for_event(locked_event),
    }
    if cancelled_registration:
        for field, value in defaults.items():
            setattr(cancelled_registration, field, value)
        cancelled_registration.save()
        return cancelled_registration, False

    return (
        EventRegistration.objects.create(
            user=user,
            event=locked_event,
            **defaults,
        ),
        True,
    )


@transaction.atomic
def cancel_event_registration(*, event: Event, user) -> EventRegistration:
    registration = (
        EventRegistration.objects.select_for_update()
        .filter(
            user=user,
            event=event,
            status__in=(
                EventRegistration.Status.REGISTERED,
                EventRegistration.Status.WAITLISTED,
            ),
        )
        .first()
    )
    if not registration:
        raise serializers.ValidationError({"event": "No active registration was found."})

    registration.status = EventRegistration.Status.CANCELLED
    registration.save(update_fields=["status", "updated_at"])
    return registration


def public_event_queryset():
    return (
        Event.objects.filter(
            moderation_status=Event.Status.PUBLISHED,
            visibility=Event.Visibility.PUBLIC,
        )
        .select_related("category", "location", "source", "organizer")
        .annotate(
            active_registration_count=Count(
                "registrations",
                filter=Q(
                    registrations__status__in=(
                        EventRegistration.Status.REGISTERED,
                        EventRegistration.Status.ATTENDED,
                    )
                ),
            )
        )
    )

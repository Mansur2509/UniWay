from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from common.validators import validate_http_url


class EventCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Event categories"

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    class Format(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"
        HYBRID = "hybrid", "Hybrid"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending review"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        ARCHIVED = "archived", "Archived"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"

    class PriceType(models.TextChoices):
        FREE = "free", "Free"
        PAID = "paid", "Paid"
        EXTERNAL = "external", "External payment"
        UNKNOWN = "unknown", "Unknown"

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="organized_events",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True)
    short_description = models.CharField(max_length=360, blank=True)
    description = models.TextField()
    organizer_name = models.CharField(max_length=180)
    format = models.CharField(max_length=20, choices=Format.choices, db_index=True)
    is_online = models.BooleanField(default=False, db_index=True)
    online_url = models.URLField(blank=True, validators=[validate_http_url])
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True, db_index=True)
    capacity = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    price_type = models.CharField(
        max_length=20,
        choices=PriceType.choices,
        default=PriceType.UNKNOWN,
        db_index=True,
    )
    price_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
    )
    cover_image_url = models.URLField(blank=True, validators=[validate_http_url])
    language = models.CharField(max_length=80, blank=True)
    eligibility = models.CharField(max_length=240, blank=True)
    is_free = models.BooleanField(default=True, db_index=True)
    scholarship_available = models.BooleanField(default=False)
    moderation_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_REVIEW,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("deadline", "starts_at")
        indexes = [
            models.Index(fields=("moderation_status", "deadline")),
            models.Index(fields=("format", "is_free")),
            models.Index(fields=("visibility", "moderation_status", "starts_at")),
        ]

    def __str__(self) -> str:
        return self.title


class EventLocation(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="location")
    country = models.CharField(max_length=100, db_index=True)
    city = models.CharField(max_length=120, blank=True, db_index=True)
    venue = models.CharField(max_length=240, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)


class EventSource(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="source")
    source_title = models.CharField(max_length=240)
    source_url = models.URLField(validators=[validate_http_url])
    is_official = models.BooleanField(default=True)
    retrieved_at = models.DateTimeField(auto_now_add=True)


class SavedEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_events")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "event"), name="unique_saved_event")
        ]


class EventSubmission(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="submission")
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="event_submissions",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)


class EventModerationLog(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="moderation_logs")
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="event_moderation_actions",
    )
    previous_status = models.CharField(max_length=20, choices=Event.Status.choices)
    new_status = models.CharField(max_length=20, choices=Event.Status.choices)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "registered", "Registered"
        CANCELLED = "cancelled", "Cancelled"
        WAITLISTED = "waitlisted", "Waitlisted"
        ATTENDED = "attended", "Attended"

    class PaymentStatus(models.TextChoices):
        NOT_REQUIRED = "not_required", "Not required"
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        WAIVED = "waived", "Waived"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED,
        db_index=True,
    )
    registration_data = models.JSONField(default=dict, blank=True)
    contact_snapshot = models.JSONField(default=dict, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_REQUIRED,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "event"),
                condition=Q(status__in=("registered", "waitlisted", "attended")),
                name="unique_active_event_registration",
            )
        ]
        indexes = [
            models.Index(fields=("event", "status")),
            models.Index(fields=("user", "status")),
        ]


class EventFormField(models.Model):
    class FieldType(models.TextChoices):
        SHORT_TEXT = "short_text", "Short text"
        LONG_TEXT = "long_text", "Long text"
        SINGLE_CHOICE = "single_choice", "Single choice"
        MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
        NUMBER = "number", "Number"
        DATE = "date", "Date"
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone"
        TELEGRAM = "telegram", "Telegram username"
        URL = "url", "File or link URL"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="form_fields")
    field_type = models.CharField(max_length=32, choices=FieldType.choices)
    label = models.CharField(max_length=160)
    help_text = models.CharField(max_length=500, blank=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    choices = models.JSONField(default=list, blank=True)
    validation = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("event", "order"),
                name="unique_event_form_field_order",
            )
        ]
        indexes = [models.Index(fields=("event", "order"))]

    def __str__(self) -> str:
        return f"{self.event_id}: {self.label}"


class EventRegistrationAnswer(models.Model):
    registration = models.ForeignKey(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    field = models.ForeignKey(
        EventFormField,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    value = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("field__order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("registration", "field"),
                name="unique_event_registration_answer",
            )
        ]

    def __str__(self) -> str:
        return f"{self.registration_id}: {self.field.label}"


class EventTicket(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"
        CHECKED_IN = "checked_in", "Checked in"
        EXPIRED = "expired", "Expired"

    registration = models.OneToOneField(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name="ticket",
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_tickets",
    )
    code = models.CharField(max_length=96, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=("event", "status")),
            models.Index(fields=("user", "status")),
        ]

    def __str__(self) -> str:
        return f"{self.event_id}:{self.registration_id}:{self.status}"


class ParticipationRecord(models.Model):
    class AttendanceStatus(models.TextChoices):
        CHECKED_IN = "checked_in", "Checked in"
        NO_SHOW = "no_show", "No show"

    class ParticipationType(models.TextChoices):
        ATTENDEE = "attendee", "Attendee"
        SPEAKER = "speaker", "Speaker"
        VOLUNTEER = "volunteer", "Volunteer"

    class VerificationStatus(models.TextChoices):
        VERIFIED = "verified", "Verified"
        REVOKED = "revoked", "Revoked"

    registration = models.OneToOneField(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name="participation_record",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participation_records",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="participation_records",
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_participation_records",
    )
    attendance_status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.CHECKED_IN,
    )
    participation_type = models.CharField(
        max_length=20,
        choices=ParticipationType.choices,
        default=ParticipationType.ATTENDEE,
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.VERIFIED,
    )
    verified_at = models.DateTimeField()
    record_id = models.UUIDField(unique=True)
    public_verification_code = models.CharField(max_length=64, unique=True, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-verified_at",)
        indexes = [
            models.Index(fields=("user", "verification_status")),
            models.Index(fields=("event", "attendance_status")),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.event_id}: {self.verification_status}"


class EventNotification(models.Model):
    class NotificationType(models.TextChoices):
        REGISTRATION_CONFIRMED = "registration_confirmed", "Registration confirmed"
        REGISTRATION_CANCELLED = "registration_cancelled", "Registration cancelled"
        EVENT_APPROVED = "event_approved", "Event approved"
        EVENT_REJECTED = "event_rejected", "Event rejected"
        ORGANIZER_NEW_REGISTRATION = "organizer_new_registration", "New registration"
        EVENT_REMINDER_PENDING = "event_reminder_pending", "Event reminder pending"
        CHECK_IN_CONFIRMED = "check_in_confirmed", "Check-in confirmed"
        PARTICIPATION_VERIFIED = "participation_verified", "Participation verified"

    class Channel(models.TextChoices):
        INTERNAL = "internal", "Internal"
        TELEGRAM = "telegram", "Telegram"

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SKIPPED = "skipped", "Skipped"
        FAILED = "failed", "Failed"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="notifications")
    registration = models.ForeignKey(
        EventRegistration,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_notifications_created",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_notifications",
    )
    notification_type = models.CharField(max_length=64, choices=NotificationType.choices)
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.INTERNAL,
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
    )
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("recipient", "status")),
            models.Index(fields=("event", "notification_type")),
        ]


class OrganizerModeration(models.Model):
    """Current staff standing for one organizer account.

    Absence of a record means "never reviewed" and is treated as allowed --
    only an explicit suspended/rejected record blocks organizer actions, so
    existing organizers are unaffected until staff actively reviews them.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    organizer = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizer_moderation"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organizer_moderation_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.organizer_id} organizer moderation ({self.status})"


class OrganizerApplication(models.Model):
    """A student's self-service application to become an event organizer.

    Deliberately separate from `OrganizerModeration` (which tracks standing
    for an account that already has the organizer role): this is the
    pre-role-change request itself, reviewed by staff via the Django admin.
    A student may have at most one PENDING application at a time (enforced
    below); once decided, they can apply again if rejected.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizer_applications"
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField()
    telegram_username = models.CharField(max_length=33)
    description = models.TextField(max_length=1000)
    project_link = models.URLField(blank=True, validators=[validate_http_url])
    motivation = models.TextField(max_length=500)
    experience = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organizer_application_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["applicant"],
                condition=Q(status="pending"),
                name="unique_pending_organizer_application_per_user",
            )
        ]

    def __str__(self) -> str:
        return f"OrganizerApplication(applicant={self.applicant_id}, {self.status})"

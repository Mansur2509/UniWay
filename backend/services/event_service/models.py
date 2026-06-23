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

from django.contrib import admin

from .models import (
    Event,
    EventCategory,
    EventFormField,
    EventLocation,
    EventModerationLog,
    EventNotification,
    EventRegistration,
    EventRegistrationAnswer,
    EventSource,
    EventSubmission,
    EventTicket,
    ParticipationRecord,
    SavedEvent,
)


class EventLocationInline(admin.StackedInline):
    model = EventLocation
    extra = 0


class EventSourceInline(admin.StackedInline):
    model = EventSource
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "format",
        "moderation_status",
        "visibility",
        "deadline",
        "capacity",
    )
    list_filter = ("moderation_status", "visibility", "format", "category", "price_type")
    search_fields = ("title", "organizer_name", "location__city")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [EventLocationInline, EventSourceInline]


admin.site.register(EventCategory)
admin.site.register(SavedEvent)
admin.site.register(EventSubmission)
admin.site.register(EventModerationLog)


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "payment_status", "created_at")
    list_filter = ("status", "payment_status")
    search_fields = ("user__email", "event__title")
    readonly_fields = ("registration_data", "contact_snapshot", "created_at", "updated_at")


@admin.register(EventFormField)
class EventFormFieldAdmin(admin.ModelAdmin):
    list_display = ("event", "label", "field_type", "is_required", "order")
    list_filter = ("field_type", "is_required")
    search_fields = ("event__title", "label")


@admin.register(EventRegistrationAnswer)
class EventRegistrationAnswerAdmin(admin.ModelAdmin):
    list_display = ("registration", "field", "created_at")
    search_fields = ("registration__user__email", "registration__event__title", "field__label")
    readonly_fields = ("value", "created_at", "updated_at")


@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = ("registration", "event", "user", "status", "created_at", "checked_in_at")
    list_filter = ("status",)
    search_fields = ("code", "user__email", "event__title")
    readonly_fields = ("code", "created_at", "checked_in_at", "expires_at")


@admin.register(ParticipationRecord)
class ParticipationRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "verification_status", "attendance_status", "verified_at")
    list_filter = ("verification_status", "attendance_status", "participation_type")
    search_fields = ("user__email", "event__title", "public_verification_code")
    readonly_fields = ("record_id", "public_verification_code", "created_at", "updated_at")


@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ("notification_type", "channel", "status", "event", "recipient", "created_at")
    list_filter = ("notification_type", "channel", "status")
    search_fields = ("event__title", "recipient__email")
    readonly_fields = ("payload", "created_at")

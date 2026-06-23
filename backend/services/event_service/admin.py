from django.contrib import admin

from .models import (
    Event,
    EventCategory,
    EventLocation,
    EventModerationLog,
    EventRegistration,
    EventSource,
    EventSubmission,
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

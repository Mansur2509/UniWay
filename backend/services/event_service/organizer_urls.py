from django.urls import path

from .views import (
    OrganizerCategoryListView,
    OrganizerEventAnalyticsView,
    OrganizerEventArchiveView,
    OrganizerEventCancelView,
    OrganizerEventCheckInView,
    OrganizerEventDetailView,
    OrganizerEventFormView,
    OrganizerEventListCreateView,
    OrganizerEventParticipantsExportView,
    OrganizerEventRegistrationListView,
    OrganizerEventSubmitView,
    OrganizerEventTicketVerifyView,
)

app_name = "organizer-events"

urlpatterns = [
    path("event-categories/", OrganizerCategoryListView.as_view(), name="categories"),
    path("events/analytics/", OrganizerEventAnalyticsView.as_view(), name="analytics"),
    path("events/", OrganizerEventListCreateView.as_view(), name="list-create"),
    path("events/<slug:slug>/", OrganizerEventDetailView.as_view(), name="detail"),
    path("events/<slug:slug>/form/", OrganizerEventFormView.as_view(), name="form"),
    path("events/<slug:slug>/submit/", OrganizerEventSubmitView.as_view(), name="submit"),
    path(
        "events/<slug:slug>/registrations/",
        OrganizerEventRegistrationListView.as_view(),
        name="registrations",
    ),
    path(
        "events/<slug:slug>/registrations/export/",
        OrganizerEventParticipantsExportView.as_view(),
        name="registrations-export",
    ),
    path(
        "events/<slug:slug>/registrations/<int:registration_id>/check-in/",
        OrganizerEventCheckInView.as_view(),
        name="registration-check-in",
    ),
    path(
        "events/<slug:slug>/tickets/verify/",
        OrganizerEventTicketVerifyView.as_view(),
        name="ticket-verify",
    ),
    path(
        "events/<slug:slug>/archive/",
        OrganizerEventArchiveView.as_view(),
        name="archive",
    ),
    path(
        "events/<slug:slug>/cancel/",
        OrganizerEventCancelView.as_view(),
        name="cancel",
    ),
]

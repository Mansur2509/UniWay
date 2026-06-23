from django.urls import path

from .views import (
    OrganizerCategoryListView,
    OrganizerEventArchiveView,
    OrganizerEventCancelView,
    OrganizerEventDetailView,
    OrganizerEventListCreateView,
    OrganizerEventRegistrationListView,
    OrganizerEventSubmitView,
)

app_name = "organizer-events"

urlpatterns = [
    path("event-categories/", OrganizerCategoryListView.as_view(), name="categories"),
    path("events/", OrganizerEventListCreateView.as_view(), name="list-create"),
    path("events/<slug:slug>/", OrganizerEventDetailView.as_view(), name="detail"),
    path("events/<slug:slug>/submit/", OrganizerEventSubmitView.as_view(), name="submit"),
    path(
        "events/<slug:slug>/registrations/",
        OrganizerEventRegistrationListView.as_view(),
        name="registrations",
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

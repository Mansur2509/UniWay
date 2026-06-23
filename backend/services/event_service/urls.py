from django.urls import path

from .views import (
    EventRegistrationCancelView,
    EventRegistrationView,
    MyEventRegistrationListView,
    PublicEventDetailView,
    PublicEventListView,
)

app_name = "events"

urlpatterns = [
    path("", PublicEventListView.as_view(), name="list"),
    path("my-registrations/", MyEventRegistrationListView.as_view(), name="my-registrations"),
    path("<slug:slug>/", PublicEventDetailView.as_view(), name="detail"),
    path("<slug:slug>/register/", EventRegistrationView.as_view(), name="register"),
    path(
        "<slug:slug>/cancel-registration/",
        EventRegistrationCancelView.as_view(),
        name="cancel-registration",
    ),
]


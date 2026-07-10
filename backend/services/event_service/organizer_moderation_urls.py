from django.urls import path

from .views import AdminOrganizerListView, AdminOrganizerModerationActionView

app_name = "organizer-moderation"

urlpatterns = [
    path("", AdminOrganizerListView.as_view(), name="list"),
    path(
        "<int:pk>/moderation/",
        AdminOrganizerModerationActionView.as_view(),
        name="moderation-action",
    ),
]

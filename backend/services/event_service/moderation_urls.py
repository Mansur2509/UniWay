from django.urls import path

from .views import (
    AdminEventApproveView,
    AdminEventArchiveView,
    AdminEventModerationLogListView,
    AdminEventRejectView,
    PendingEventModerationListView,
)

app_name = "event-moderation"

urlpatterns = [
    path("pending/", PendingEventModerationListView.as_view(), name="pending"),
    path("<slug:slug>/approve/", AdminEventApproveView.as_view(), name="approve"),
    path("<slug:slug>/reject/", AdminEventRejectView.as_view(), name="reject"),
    path("<slug:slug>/archive/", AdminEventArchiveView.as_view(), name="archive"),
    path("<slug:slug>/logs/", AdminEventModerationLogListView.as_view(), name="logs"),
]

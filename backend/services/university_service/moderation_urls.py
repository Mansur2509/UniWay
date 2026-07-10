from django.urls import path

from .views import AdminUniversityModerationActionView, AdminUniversityReviewQueueView

app_name = "university-moderation"

urlpatterns = [
    path("review-queue/", AdminUniversityReviewQueueView.as_view(), name="review-queue"),
    path(
        "<int:pk>/moderation/",
        AdminUniversityModerationActionView.as_view(),
        name="moderation-action",
    ),
]

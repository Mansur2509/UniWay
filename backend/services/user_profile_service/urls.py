from django.urls import path

from .views import (
    ApplicationReadinessView,
    CompleteOnboardingView,
    CurrentProfileView,
    ProfileCompletionView,
)

app_name = "profile"

urlpatterns = [
    path("me/", CurrentProfileView.as_view(), name="me"),
    path("completion/", ProfileCompletionView.as_view(), name="completion"),
    path("complete-onboarding/", CompleteOnboardingView.as_view(), name="complete-onboarding"),
    path("readiness/", ApplicationReadinessView.as_view(), name="readiness"),
]

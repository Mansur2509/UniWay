from django.urls import path

from .views import AdminRunProfileAssessmentView

app_name = "admin_profile_assessment"

urlpatterns = [
    path(
        "<int:user_id>/profile-assessment/run/",
        AdminRunProfileAssessmentView.as_view(),
        name="run",
    ),
]

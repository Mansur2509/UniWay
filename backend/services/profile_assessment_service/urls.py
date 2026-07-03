from django.urls import path

from .views import LatestProfileAssessmentView, RunProfileAssessmentView

app_name = "profile_assessment"

urlpatterns = [
    path("latest/", LatestProfileAssessmentView.as_view(), name="latest"),
    path("run/", RunProfileAssessmentView.as_view(), name="run"),
]

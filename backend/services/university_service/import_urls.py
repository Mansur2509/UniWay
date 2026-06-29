from django.urls import path

from .views import (
    AdminUniversityImportDryRunView,
    AdminUniversityImportExecuteView,
    AdminUniversityImportJobDetailView,
)

app_name = "university-import"

urlpatterns = [
    path("dry-run/", AdminUniversityImportDryRunView.as_view(), name="dry-run"),
    path("execute/", AdminUniversityImportExecuteView.as_view(), name="execute"),
    path("jobs/<int:pk>/", AdminUniversityImportJobDetailView.as_view(), name="job-detail"),
]

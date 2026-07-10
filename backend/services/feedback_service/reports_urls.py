from django.urls import path

from .views import UserReportCreateView

app_name = "reports"

urlpatterns = [
    path("", UserReportCreateView.as_view(), name="create"),
]

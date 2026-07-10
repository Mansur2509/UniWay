from django.urls import path

from .views import AdminUserReportDetailView, AdminUserReportListView

app_name = "admin-reports"

urlpatterns = [
    path("", AdminUserReportListView.as_view(), name="list"),
    path("<int:pk>/", AdminUserReportDetailView.as_view(), name="detail"),
]

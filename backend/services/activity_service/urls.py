from django.urls import path

from .views import MyAnalyticsView

app_name = "analytics"

urlpatterns = [
    path("me/", MyAnalyticsView.as_view(), name="me"),
]

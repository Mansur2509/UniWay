from django.urls import path

from .views import (
    AdminAnalyticsActivityView,
    AdminAnalyticsFeatureUsageView,
    AdminAnalyticsSummaryView,
)

app_name = "admin-analytics"

urlpatterns = [
    path("summary/", AdminAnalyticsSummaryView.as_view(), name="summary"),
    path("feature-usage/", AdminAnalyticsFeatureUsageView.as_view(), name="feature-usage"),
    path("activity/", AdminAnalyticsActivityView.as_view(), name="activity"),
]

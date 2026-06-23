from django.urls import path

from .views import MentorPlaceholderView

urlpatterns = [
    path("mentor/", MentorPlaceholderView.as_view(), name="ai-mentor"),
]


from django.urls import path

from .views import OrganizerApplicationCreateView, OrganizerApplicationMineView

app_name = "organizer-applications"

urlpatterns = [
    path("", OrganizerApplicationCreateView.as_view(), name="create"),
    path("mine/", OrganizerApplicationMineView.as_view(), name="mine"),
]

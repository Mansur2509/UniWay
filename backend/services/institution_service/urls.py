from django.urls import path

from .views import (
    AcceptInvitationView,
    InstitutionAnalyticsView,
    InstitutionCreateView,
    InstitutionInvitationView,
    InstitutionStudentsView,
    MyMembershipView,
)

app_name = "institutions"

urlpatterns = [
    path("", InstitutionCreateView.as_view(), name="create"),
    path("<slug:slug>/invitations/", InstitutionInvitationView.as_view(), name="invite"),
    path("<slug:slug>/memberships/mine/", MyMembershipView.as_view(), name="my-membership"),
    path(
        "<slug:slug>/memberships/mine/accept/",
        AcceptInvitationView.as_view(),
        name="accept-invitation",
    ),
    path("<slug:slug>/students/", InstitutionStudentsView.as_view(), name="students"),
    path("<slug:slug>/analytics/", InstitutionAnalyticsView.as_view(), name="analytics"),
]

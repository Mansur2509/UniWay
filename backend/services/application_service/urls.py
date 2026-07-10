from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ApplicationDocumentViewSet,
    ApplicationMilestoneViewSet,
    ApplicationRecommendationViewSet,
    ApplicationRequirementViewSet,
    ApplicationTrackerViewSet,
)

app_name = "applications"

router = DefaultRouter()
router.register("milestones", ApplicationMilestoneViewSet, basename="application-milestone")
router.register("requirements", ApplicationRequirementViewSet, basename="application-requirement")
router.register(
    "recommendations", ApplicationRecommendationViewSet, basename="application-recommendation"
)
router.register("documents", ApplicationDocumentViewSet, basename="application-document")
router.register("", ApplicationTrackerViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]

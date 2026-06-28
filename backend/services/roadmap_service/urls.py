from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GenerateRoadmapView, RoadmapPlanView, RoadmapTaskViewSet

app_name = "roadmap"

router = DefaultRouter()
router.register("tasks", RoadmapTaskViewSet, basename="roadmap-task")

urlpatterns = [
    path("generate/", GenerateRoadmapView.as_view(), name="generate"),
    path("", RoadmapPlanView.as_view(), name="plan"),
    path("", include(router.urls)),
]

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole
from services.application_service.models import ApplicationTrackerItem
from services.essay_service.models import AIEssayScoreReport
from services.roadmap_service.models import RoadmapTask
from services.user_profile_service.services import (
    calculate_profile_completion,
    ensure_profile_records,
)

from .models import AnalyticsEvent
from .serializers import AdminAnalyticsSummarySerializer, UserAnalyticsSerializer

User = get_user_model()


class MyAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, preferences = ensure_profile_records(user)
        completion = calculate_profile_completion(profile, preferences)

        roadmap_tasks = RoadmapTask.objects.filter(user=user)
        applications = ApplicationTrackerItem.objects.filter(user=user)
        applications_by_status = dict(
            applications.values("status").annotate(count=Count("id")).values_list(
                "status", "count"
            )
        )
        upcoming_cutoff = timezone.now().date() + timedelta(days=30)
        upcoming_deadlines_count = applications.filter(
            deadline__isnull=False,
            deadline__gte=timezone.now().date(),
            deadline__lte=upcoming_cutoff,
        ).count()

        activity_by_type = dict(
            AnalyticsEvent.objects.filter(user=user)
            .values("event_type")
            .annotate(count=Count("id"))
            .values_list("event_type", "count")
        )

        data = {
            "profile_completion_percent": completion.percentage,
            "roadmap_tasks_completed": roadmap_tasks.filter(
                status=RoadmapTask.Status.COMPLETED
            ).count(),
            "roadmap_tasks_total": roadmap_tasks.count(),
            "applications_by_status": applications_by_status,
            "essay_reviews_count": AIEssayScoreReport.objects.filter(user=user).count(),
            "upcoming_deadlines_count": upcoming_deadlines_count,
            "activity_by_type": activity_by_type,
        }
        return Response(UserAnalyticsSerializer(data).data)


class AdminAnalyticsSummaryView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        now = timezone.now()
        since_7d = now - timedelta(days=7)
        since_30d = now - timedelta(days=30)

        active_7d = (
            AnalyticsEvent.objects.filter(created_at__gte=since_7d, user__isnull=False)
            .values("user_id")
            .distinct()
            .count()
        )
        active_30d = (
            AnalyticsEvent.objects.filter(created_at__gte=since_30d, user__isnull=False)
            .values("user_id")
            .distinct()
            .count()
        )
        retained = (
            AnalyticsEvent.objects.filter(user__isnull=False)
            .values("user_id")
            .annotate(count=Count("id"))
            .filter(count__gte=2)
            .count()
        )

        data = {
            "total_users": User.objects.count(),
            "new_users_7d": User.objects.filter(date_joined__gte=since_7d).count(),
            "new_users_30d": User.objects.filter(date_joined__gte=since_30d).count(),
            "active_users_7d": active_7d,
            "active_users_30d": active_30d,
            "applications_created_total": AnalyticsEvent.objects.filter(
                event_type=AnalyticsEvent.EventType.APPLICATION_CREATED
            ).count(),
            "universities_shortlisted_total": AnalyticsEvent.objects.filter(
                event_type=AnalyticsEvent.EventType.UNIVERSITY_SHORTLISTED
            ).count(),
            "essay_reviews_requested_total": AnalyticsEvent.objects.filter(
                event_type=AnalyticsEvent.EventType.ESSAY_REVIEW_REQUESTED
            ).count(),
            "roadmap_generations_total": AnalyticsEvent.objects.filter(
                event_type=AnalyticsEvent.EventType.ROADMAP_GENERATED
            ).count(),
            "event_registrations_total": AnalyticsEvent.objects.filter(
                event_type=AnalyticsEvent.EventType.EVENT_REGISTERED
            ).count(),
            "organizer_events_created_total": AnalyticsEvent.objects.filter(
                event_type=AnalyticsEvent.EventType.ORGANIZER_EVENT_CREATED
            ).count(),
            "retained_users_2plus_actions": retained,
        }
        return Response(AdminAnalyticsSummarySerializer(data).data)


class AdminAnalyticsFeatureUsageView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        counts = (
            AnalyticsEvent.objects.values("event_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return Response({row["event_type"]: row["count"] for row in counts})


class AdminAnalyticsActivityView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        since = timezone.now() - timedelta(days=30)
        rows = (
            AnalyticsEvent.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        daily_counts = {row["day"].isoformat(): row["count"] for row in rows}
        return Response({"daily_event_counts": daily_counts})

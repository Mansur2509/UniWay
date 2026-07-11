from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APITestCase

from services.activity_service.models import AnalyticsEvent
from services.activity_service.services import track_event
from services.roadmap_service.models import RoadmapPlan, RoadmapTask
from services.university_service.models import University
from services.user_profile_service.services import ensure_profile_records

User = get_user_model()

MY_ANALYTICS_URL = "/api/v1/analytics/me/"
ADMIN_SUMMARY_URL = "/api/v1/admin/analytics/summary/"
ADMIN_FEATURE_USAGE_URL = "/api/v1/admin/analytics/feature-usage/"
ADMIN_ACTIVITY_URL = "/api/v1/admin/analytics/activity/"


def create_university(slug="test-university", **overrides):
    defaults = {
        "name": "Test University",
        "country": "Demoland",
        "city": "Sample City",
        "official_website": f"https://example.com/{slug}",
        "is_published": True,
    }
    defaults.update(overrides)
    return University.objects.create(slug=slug, **defaults)


class TrackEventSanitizationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
        )

    def test_long_string_metadata_is_truncated(self):
        long_text = "x" * 5000
        event = track_event(
            user=self.user,
            event_type=AnalyticsEvent.EventType.ESSAY_REVIEW_REQUESTED,
            metadata={"draft_text": long_text},
        )
        self.assertLess(len(event.metadata["draft_text"]), 300)

    def test_nested_metadata_is_dropped(self):
        event = track_event(
            user=self.user,
            event_type=AnalyticsEvent.EventType.PROFILE_UPDATED,
            metadata={"profile_snapshot": {"full_name": "A", "gpa": 3.9}, "safe": "ok"},
        )
        self.assertNotIn("profile_snapshot", event.metadata)
        self.assertEqual(event.metadata["safe"], "ok")

    def test_anonymous_event_has_no_user(self):
        event = track_event(user=None, event_type=AnalyticsEvent.EventType.USER_REGISTERED)
        self.assertIsNone(event.user)


class ProfileUpdateTrackingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
        )
        self.client.force_authenticate(self.user)

    def test_profile_update_creates_analytics_event(self):
        response = self.client.patch(
            "/api/profile/me/", {"full_name": "Updated Name"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(
            AnalyticsEvent.objects.filter(
                user=self.user, event_type=AnalyticsEvent.EventType.PROFILE_UPDATED
            ).exists()
        )


class ApplicationCreationTrackingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
        )
        self.university = create_university()
        self.client.force_authenticate(self.user)

    def test_application_creation_creates_analytics_event(self):
        response = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        event = AnalyticsEvent.objects.get(
            user=self.user, event_type=AnalyticsEvent.EventType.APPLICATION_CREATED
        )
        self.assertEqual(event.entity_id, response.data["id"])


class RoadmapTaskCompletionTrackingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
        )
        self.plan = RoadmapPlan.objects.create(user=self.user, title="My roadmap")
        self.task = RoadmapTask.objects.create(
            user=self.user,
            plan=self.plan,
            title="Request letters",
            category=RoadmapTask.Category.RECOMMENDATIONS,
            dedup_key="manual:1",
        )
        self.client.force_authenticate(self.user)

    def test_marking_task_completed_creates_analytics_event(self):
        response = self.client.patch(
            f"/api/v1/roadmaps/tasks/{self.task.id}/", {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(
            AnalyticsEvent.objects.filter(
                user=self.user,
                event_type=AnalyticsEvent.EventType.ROADMAP_TASK_COMPLETED,
                entity_id=self.task.id,
            ).exists()
        )

    def test_marking_task_completed_twice_does_not_duplicate(self):
        self.client.patch(
            f"/api/v1/roadmaps/tasks/{self.task.id}/", {"status": "completed"}, format="json"
        )
        self.client.patch(
            f"/api/v1/roadmaps/tasks/{self.task.id}/", {"notes": "still done"}, format="json"
        )
        self.assertEqual(
            AnalyticsEvent.objects.filter(
                event_type=AnalyticsEvent.EventType.ROADMAP_TASK_COMPLETED
            ).count(),
            1,
        )


class MyAnalyticsApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="student1@example.com",
            email="student1@example.com",
            password="Strong-Development-Password-842!",
        )
        self.user2 = User.objects.create_user(
            username="student2@example.com",
            email="student2@example.com",
            password="Strong-Development-Password-842!",
        )

    def test_anonymous_cannot_access_my_analytics(self):
        response = self.client.get(MY_ANALYTICS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_activity(self):
        track_event(user=self.user1, event_type=AnalyticsEvent.EventType.UNIVERSITY_SHORTLISTED)
        track_event(user=self.user2, event_type=AnalyticsEvent.EventType.UNIVERSITY_SHORTLISTED)
        track_event(user=self.user2, event_type=AnalyticsEvent.EventType.UNIVERSITY_SHORTLISTED)

        self.client.force_authenticate(self.user1)
        response = self.client.get(MY_ANALYTICS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["activity_by_type"].get("university_shortlisted"), 1
        )

    def test_response_includes_profile_completion_and_roadmap_progress(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(MY_ANALYTICS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("profile_completion_percent", response.data)
        self.assertIn("roadmap_tasks_completed", response.data)
        self.assertIn("applications_by_status", response.data)
        self.assertIn("essay_reviews_count", response.data)

    def test_query_count_does_not_grow_with_activity_event_count(self):
        # PERFORMANCE-011 PART 4: MyAnalyticsView aggregates with Count(), so
        # more AnalyticsEvent rows must not mean more queries. Profile/
        # preference rows are created lazily on first access (see
        # ensure_profile_records), so warm those up first -- otherwise the
        # first measured request looks artificially heavier for an unrelated
        # reason and masks the thing this test actually checks.
        ensure_profile_records(self.user1)
        self.client.force_authenticate(self.user1)
        for _ in range(3):
            track_event(user=self.user1, event_type=AnalyticsEvent.EventType.UNIVERSITY_SHORTLISTED)
        with CaptureQueriesContext(connection) as few:
            self.client.get(MY_ANALYTICS_URL)

        for _ in range(30):
            track_event(user=self.user1, event_type=AnalyticsEvent.EventType.UNIVERSITY_SHORTLISTED)
        with CaptureQueriesContext(connection) as many:
            self.client.get(MY_ANALYTICS_URL)

        self.assertEqual(
            len(few),
            len(many),
            f"{MY_ANALYTICS_URL} query count grew with activity event count -- check for a new N+1.",
        )


class AdminAnalyticsPermissionTests(APITestCase):
    def setUp(self):
        cache.clear()  # admin analytics summary/feature-usage/activity are cached.
        self.student = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )
        self.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ADMIN,
        )

    def test_student_cannot_access_admin_summary(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(ADMIN_SUMMARY_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_access_feature_usage(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(ADMIN_FEATURE_USAGE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_access_activity(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(ADMIN_ACTIVITY_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_sees_aggregate_summary(self):
        track_event(user=self.student, event_type=AnalyticsEvent.EventType.APPLICATION_CREATED)
        self.client.force_authenticate(self.admin)
        response = self.client.get(ADMIN_SUMMARY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["total_users"], 2)
        self.assertEqual(response.data["applications_created_total"], 1)

    def test_admin_feature_usage_returns_counts_by_event_type(self):
        track_event(user=self.student, event_type=AnalyticsEvent.EventType.ROADMAP_GENERATED)
        track_event(user=self.student, event_type=AnalyticsEvent.EventType.ROADMAP_GENERATED)
        self.client.force_authenticate(self.admin)
        response = self.client.get(ADMIN_FEATURE_USAGE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["roadmap_generated"], 2)

    def test_retained_users_counts_two_plus_actions(self):
        track_event(user=self.student, event_type=AnalyticsEvent.EventType.ROADMAP_GENERATED)
        track_event(user=self.student, event_type=AnalyticsEvent.EventType.ESSAY_REVIEW_REQUESTED)
        self.client.force_authenticate(self.admin)
        response = self.client.get(ADMIN_SUMMARY_URL)
        self.assertEqual(response.data["retained_users_2plus_actions"], 1)

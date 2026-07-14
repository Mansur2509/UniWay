from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APITestCase

from services.application_service.models import ApplicationRequirement, ApplicationTrackerItem
from services.essay_service.models import EssayWorkspace
from services.roadmap_service.models import RoadmapPlan, RoadmapTask
from services.university_service.models import (
    University,
    UniversityDataSource,
    UniversityFieldVerification,
    UniversityProgram,
)
from services.user_profile_service.models import Recommender

User = get_user_model()


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


class ApplicationTrackerApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="applicant1", email="applicant1@test.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="applicant2", email="applicant2@test.com", password="testpass123"
        )
        self.university = create_university()

    def test_list_requires_authentication(self):
        response = self.client.get("/api/applications/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_application(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["status"], ApplicationTrackerItem.Status.RESEARCHING)
        self.assertEqual(response.data["university_name"], self.university.name)

    def test_target_metadata_and_verified_regular_deadline_are_serialized(self):
        self.university.application_deadline = date(2026, 11, 1)
        self.university.save(update_fields=["application_deadline"])
        source_url = "https://example.com/admissions/deadlines"
        UniversityFieldVerification.objects.create(
            university=self.university,
            field_name="application_deadline",
            status=UniversityFieldVerification.Status.VERIFIED,
            source_url=source_url,
            last_verified_date=date.today(),
        )
        UniversityDataSource.objects.create(
            university=self.university,
            source_title="First-year application deadlines",
            source_url=source_url,
        )
        program = UniversityProgram.objects.create(
            university=self.university,
            name="Economics",
            degree_level="undergraduate",
        )
        self.client.force_authenticate(self.user1)

        response = self.client.post(
            "/api/applications/",
            {
                "university": self.university.id,
                "target_program": program.id,
                "target_intake_year": 2027,
                "application_round": "regular_decision",
                "personal_estimated_deadline": "2026-10-25",
                "priority": "high",
                "notes": "Confirm the official checklist before submitting.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["target_program_name"], "Economics")
        self.assertEqual(response.data["target_intake_year"], 2027)
        self.assertEqual(response.data["personal_estimated_deadline"], "2026-10-25")
        self.assertEqual(response.data["official_deadline"]["status"], "verified")
        self.assertEqual(response.data["official_deadline"]["date"], "2026-11-01")
        self.assertEqual(
            response.data["official_deadline"]["source_title"],
            "First-year application deadlines",
        )

    def test_stale_cycle_deadline_is_not_returned_as_current_exact_date(self):
        self.university.application_deadline = date(2025, 11, 1)
        self.university.save(update_fields=["application_deadline"])
        UniversityFieldVerification.objects.create(
            university=self.university,
            field_name="application_deadline",
            status=UniversityFieldVerification.Status.VERIFIED,
            source_url="https://example.com/admissions/deadlines",
            last_verified_date=date.today(),
        )
        self.client.force_authenticate(self.user1)

        response = self.client.post(
            "/api/applications/",
            {
                "university": self.university.id,
                "target_intake_year": 2027,
                "application_round": "regular_decision",
            },
            format="json",
        )

        self.assertEqual(response.data["official_deadline"]["status"], "outdated")
        self.assertIsNone(response.data["official_deadline"]["date"])
        self.assertEqual(response.data["official_deadline"]["source_date"], "2025-11-01")

    def test_program_must_belong_to_selected_university(self):
        other = create_university(slug="other-program-university")
        program = UniversityProgram.objects.create(
            university=other,
            name="Computer Science",
            degree_level="undergraduate",
        )
        self.client.force_authenticate(self.user1)

        response = self.client.post(
            "/api/applications/",
            {"university": self.university.id, "target_program": program.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("target_program", response.data)

    def test_duplicate_application_for_same_university_is_rejected(self):
        self.client.force_authenticate(self.user1)
        self.client.post("/api/applications/", {"university": self.university.id}, format="json")
        response = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_applications_are_self_only(self):
        self.client.force_authenticate(self.user1)
        self.client.post("/api/applications/", {"university": self.university.id}, format="json")

        self.client.force_authenticate(self.user2)
        response = self.client.get("/api/applications/")
        self.assertEqual(response.data["results"], [])

    def test_delete_archives_without_deleting_and_allows_a_new_active_target(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )

        archived = self.client.delete(f"/api/applications/{created.data['id']}/")

        self.assertEqual(archived.status_code, status.HTTP_204_NO_CONTENT)
        stored = ApplicationTrackerItem.objects.get(pk=created.data["id"])
        self.assertIsNotNone(stored.archived_at)
        active_list = self.client.get("/api/applications/")
        self.assertEqual(active_list.data["results"], [])
        recreated = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertEqual(recreated.status_code, status.HTTP_201_CREATED, recreated.data)

    def test_restore_reactivates_archived_application(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]
        self.client.delete(f"/api/applications/{application_id}/")

        response = self.client.post(f"/api/applications/{application_id}/restore/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIsNone(response.data["archived_at"])
        stored = ApplicationTrackerItem.objects.get(pk=application_id)
        self.assertIsNone(stored.archived_at)
        active_list = self.client.get("/api/applications/")
        self.assertEqual(len(active_list.data["results"]), 1)

    def test_cannot_restore_another_users_application(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]
        self.client.delete(f"/api/applications/{application_id}/")

        self.client.force_authenticate(self.user2)
        response = self.client.post(f"/api/applications/{application_id}/restore/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        stored = ApplicationTrackerItem.objects.get(pk=application_id)
        self.assertIsNotNone(stored.archived_at)

    def test_restore_nonexistent_application_returns_404(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post("/api/applications/999999/restore/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_restore_rejected_when_duplicate_active_target_exists(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]
        self.client.delete(f"/api/applications/{application_id}/")
        self.client.post("/api/applications/", {"university": self.university.id}, format="json")

        response = self.client.post(f"/api/applications/{application_id}/restore/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        stored = ApplicationTrackerItem.objects.get(pk=application_id)
        self.assertIsNotNone(stored.archived_at)

    def test_restore_requires_authentication(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]
        self.client.delete(f"/api/applications/{application_id}/")

        self.client.force_authenticate(None)
        response = self.client.post(f"/api/applications/{application_id}/restore/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_query_count_does_not_grow_per_application(self):
        # PERFORMANCE-011 PART 4: guards the select_related/prefetch_related
        # on ApplicationTrackerViewSet.get_queryset -- without it, milestones
        # and requirements would be an extra query per application (N+1).
        self.client.force_authenticate(self.user1)
        for index in range(3):
            university = create_university(slug=f"query-count-university-{index}")
            application = ApplicationTrackerItem.objects.create(
                user=self.user1, university=university
            )
            application.milestones.create(title="Submit essay", due_date=date.today())
            ApplicationRequirement.objects.create(
                application=application, requirement_type=ApplicationRequirement.RequirementType.ESSAY
            )

        with CaptureQueriesContext(connection) as few:
            self.client.get("/api/applications/")

        for index in range(3, 6):
            university = create_university(slug=f"query-count-university-{index}")
            application = ApplicationTrackerItem.objects.create(
                user=self.user1, university=university
            )
            application.milestones.create(title="Submit essay", due_date=date.today())
            ApplicationRequirement.objects.create(
                application=application, requirement_type=ApplicationRequirement.RequirementType.ESSAY
            )

        with CaptureQueriesContext(connection) as many:
            self.client.get("/api/applications/")

        self.assertEqual(
            len(few),
            len(many),
            "GET /api/applications/ query count grew with application count -- check for a new N+1.",
        )

    def test_cannot_access_another_users_application(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]

        self.client.force_authenticate(self.user2)
        response = self.client.get(f"/api/applications/{application_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_status_transition(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]

        response = self.client.patch(
            f"/api/applications/{application_id}/", {"status": "preparing"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "preparing")

    def test_creating_application_does_not_force_applying_status(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertNotEqual(response.data["status"], "applying")

    def test_deadline_missing_is_reported_as_null(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertIsNone(response.data["deadline"])

    def test_create_and_list_milestones(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]

        response = self.client.post(
            f"/api/applications/{application_id}/milestones/",
            {
                "title": "Request recommendation letters",
                "category": "recommendations",
                "due_date": (date.today() + timedelta(days=30)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        list_response = self.client.get(f"/api/applications/{application_id}/milestones/")
        self.assertEqual(len(list_response.data), 1)

    def test_update_milestone_status(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]
        milestone = self.client.post(
            f"/api/applications/{application_id}/milestones/",
            {"title": "Submit essays", "category": "essays"},
            format="json",
        )
        milestone_id = milestone.data["id"]

        response = self.client.patch(
            f"/api/applications/milestones/{milestone_id}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["status"], "completed")

    def test_cannot_update_another_users_milestone(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]
        milestone = self.client.post(
            f"/api/applications/{application_id}/milestones/",
            {"title": "Submit essays", "category": "essays"},
            format="json",
        )
        milestone_id = milestone.data["id"]

        self.client.force_authenticate(self.user2)
        response = self.client.patch(
            f"/api/applications/milestones/{milestone_id}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_milestone_can_link_to_own_roadmap_task(self):
        self.client.force_authenticate(self.user1)
        plan = RoadmapPlan.objects.create(user=self.user1, title="My roadmap")
        task = RoadmapTask.objects.create(
            user=self.user1,
            plan=plan,
            title="Request letters",
            category=RoadmapTask.Category.RECOMMENDATIONS,
            dedup_key="manual:1",
        )
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]

        response = self.client.post(
            f"/api/applications/{application_id}/milestones/",
            {
                "title": "Request letters",
                "category": "recommendations",
                "linked_roadmap_task": task.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["linked_roadmap_task"], task.id)

    def test_milestone_cannot_link_to_another_users_roadmap_task(self):
        plan = RoadmapPlan.objects.create(user=self.user2, title="Other roadmap")
        task = RoadmapTask.objects.create(
            user=self.user2,
            plan=plan,
            title="Other task",
            category=RoadmapTask.Category.RECOMMENDATIONS,
            dedup_key="manual:2",
        )

        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]

        response = self.client.post(
            f"/api/applications/{application_id}/milestones/",
            {"title": "Borrow", "category": "recommendations", "linked_roadmap_task": task.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_application(self):
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        application_id = created.data["id"]
        response = self.client.delete(f"/api/applications/{application_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_fit_tier_is_unknown_without_enough_university_data(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertEqual(response.data["fit_tier"], "unknown")

    def test_fit_tier_cannot_be_set_directly_by_client(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            "/api/applications/",
            {"university": self.university.id, "fit_tier": "safety"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["fit_tier"], "unknown")

    def test_source_defaults_to_user_added(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.assertEqual(response.data["source"], "user_added")

    def test_source_can_be_set_on_create(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            "/api/applications/",
            {"university": self.university.id, "source": "recommendation"},
            format="json",
        )
        self.assertEqual(response.data["source"], "recommendation")


class ApplicationRequirementApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="reqapplicant1", email="reqapplicant1@test.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="reqapplicant2", email="reqapplicant2@test.com", password="testpass123"
        )
        self.university = create_university(
            slug="requirement-university",
            essay_requirements="Personal statement (650 words) and one supplement.",
            ap_recommendations="Two academic recommendation letters.",
            test_policy="required",
        )
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.application_id = created.data["id"]

    def test_generate_requirements_seeds_rows_from_university_data(self):
        response = self.client.post(
            f"/api/applications/{self.application_id}/generate-requirements/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        types = {row["requirement_type"] for row in response.data}
        self.assertIn("application_fee", types)
        self.assertIn("transcript", types)
        self.assertIn("essay", types)
        self.assertIn("recommendation", types)
        self.assertIn("test_scores", types)

    def test_generate_requirements_is_idempotent(self):
        first = self.client.post(f"/api/applications/{self.application_id}/generate-requirements/")
        second = self.client.post(f"/api/applications/{self.application_id}/generate-requirements/")
        self.assertEqual(len(first.data), len(second.data))
        self.assertEqual(
            ApplicationRequirement.objects.filter(application_id=self.application_id).count(),
            len(first.data),
        )

    def test_user_can_add_custom_requirement(self):
        response = self.client.post(
            f"/api/applications/{self.application_id}/requirements/",
            {"requirement_type": "portfolio", "title": "Art portfolio"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["source"], "user_created")

    def test_update_requirement_status(self):
        created = self.client.post(
            f"/api/applications/{self.application_id}/requirements/",
            {"requirement_type": "portfolio", "title": "Art portfolio"},
            format="json",
        )
        requirement_id = created.data["id"]

        response = self.client.patch(
            f"/api/applications/requirements/{requirement_id}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["status"], "completed")

    def test_cannot_update_another_users_requirement(self):
        created = self.client.post(
            f"/api/applications/{self.application_id}/requirements/",
            {"requirement_type": "portfolio", "title": "Art portfolio"},
            format="json",
        )
        requirement_id = created.data["id"]

        self.client.force_authenticate(self.user2)
        response = self.client.patch(
            f"/api/applications/requirements/{requirement_id}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_checklist_progress_reflects_requirement_statuses(self):
        self.client.post(
            f"/api/applications/{self.application_id}/requirements/",
            {"requirement_type": "portfolio", "title": "Art portfolio"},
            format="json",
        )
        second = self.client.post(
            f"/api/applications/{self.application_id}/requirements/",
            {"requirement_type": "passport", "title": "Passport copy"},
            format="json",
        )
        self.client.patch(
            f"/api/applications/requirements/{second.data['id']}/",
            {"status": "completed"},
            format="json",
        )

        response = self.client.get(f"/api/applications/{self.application_id}/")
        self.assertEqual(response.data["checklist_progress"]["total"], 2)
        self.assertEqual(response.data["checklist_progress"]["completed"], 1)
        self.assertEqual(response.data["checklist_progress"]["percent"], 50)


class ApplicationRecommendationApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="recapplicant1", email="recapplicant1@test.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="recapplicant2", email="recapplicant2@test.com", password="testpass123"
        )
        self.university = create_university(slug="recommendation-university")
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.application_id = created.data["id"]

    def test_create_recommendation_with_plain_text_name(self):
        response = self.client.post(
            f"/api/applications/{self.application_id}/recommendations/",
            {"recommender_name": "Ms. Rivera", "recommender_role": "Chemistry teacher"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["status"], "not_requested")

    def test_create_recommendation_requires_name_or_linked_recommender(self):
        response = self.client.post(
            f"/api/applications/{self.application_id}/recommendations/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_linked_to_own_profile_recommender(self):
        recommender = Recommender.objects.create(user=self.user1, name="Dr. Lee")
        response = self.client.post(
            f"/api/applications/{self.application_id}/recommendations/",
            {"recommender": recommender.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["recommender_display_name"], "Dr. Lee")

    def test_cannot_link_another_users_profile_recommender(self):
        recommender = Recommender.objects.create(user=self.user2, name="Dr. Other")
        response = self.client.post(
            f"/api/applications/{self.application_id}/recommendations/",
            {"recommender": recommender.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_recommendation_status(self):
        created = self.client.post(
            f"/api/applications/{self.application_id}/recommendations/",
            {"recommender_name": "Ms. Rivera"},
            format="json",
        )
        response = self.client.patch(
            f"/api/applications/recommendations/{created.data['id']}/",
            {"status": "requested"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["status"], "requested")

    def test_cannot_access_another_users_recommendation(self):
        created = self.client.post(
            f"/api/applications/{self.application_id}/recommendations/",
            {"recommender_name": "Ms. Rivera"},
            format="json",
        )
        self.client.force_authenticate(self.user2)
        response = self.client.get(
            f"/api/applications/recommendations/{created.data['id']}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ApplicationDocumentApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="docapplicant1", email="docapplicant1@test.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="docapplicant2", email="docapplicant2@test.com", password="testpass123"
        )
        self.university = create_university(slug="document-university")
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.application_id = created.data["id"]

    def test_create_and_list_documents(self):
        response = self.client.post(
            f"/api/applications/{self.application_id}/documents/",
            {"document_type": "passport", "title": "Passport scan"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        listed = self.client.get(f"/api/applications/{self.application_id}/documents/")
        self.assertEqual(len(listed.data), 1)

    def test_update_document_status(self):
        created = self.client.post(
            f"/api/applications/{self.application_id}/documents/",
            {"document_type": "transcript", "title": "Transcript"},
            format="json",
        )
        response = self.client.patch(
            f"/api/applications/documents/{created.data['id']}/",
            {"status": "uploaded"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["status"], "uploaded")

    def test_cannot_access_another_users_document(self):
        created = self.client.post(
            f"/api/applications/{self.application_id}/documents/",
            {"document_type": "transcript", "title": "Transcript"},
            format="json",
        )
        self.client.force_authenticate(self.user2)
        response = self.client.get(f"/api/applications/documents/{created.data['id']}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ApplicationEssaySubresourceApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="essayapplicant1", email="essayapplicant1@test.com", password="testpass123"
        )
        self.university = create_university(slug="essay-sub-university")
        self.client.force_authenticate(self.user1)
        created = self.client.post(
            "/api/applications/", {"university": self.university.id}, format="json"
        )
        self.application_id = created.data["id"]

    def test_create_essay_under_application_infers_university(self):
        response = self.client.post(
            f"/api/applications/{self.application_id}/essays/",
            {"title": "Why this school", "essay_type": "why_school"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["university"], self.university.id)
        self.assertEqual(response.data["application"], self.application_id)

    def test_list_essays_scoped_to_application(self):
        self.client.post(
            f"/api/applications/{self.application_id}/essays/",
            {"title": "Why this school", "essay_type": "why_school"},
            format="json",
        )
        other_university = create_university(slug="essay-sub-other")
        EssayWorkspace.objects.create(
            user=self.user1, title="Unrelated essay", university=other_university
        )

        response = self.client.get(f"/api/applications/{self.application_id}/essays/")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Why this school")

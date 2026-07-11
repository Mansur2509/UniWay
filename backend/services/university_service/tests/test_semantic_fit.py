from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APITestCase

from services.ai_gateway_service.exceptions import AIProviderError, AIProviderUnavailable
from services.university_service.models import UniversitySemanticFit
from services.university_service.semantic_fit import (
    map_tier,
    refresh_semantic_fit,
    semantic_fit_status,
)
from services.user_profile_service.services import ensure_profile_records

from .test_universities import create_university

User = get_user_model()


class FakeSemanticFitClient:
    """Controllable stand-in for GeminiSemanticFitClient (mirrors the
    FakeEssayScoringClient pattern used in essay_service's tests)."""

    provider_name = "gemini"
    model_name = "fake-semantic-fit-model"

    def __init__(self, responses=None, error=None):
        self.responses = list(responses or [])
        self.error = error
        self.calls = 0

    def generate_semantic_fit(self, *, system_prompt, user_prompt, response_schema=None):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.responses.pop(0)


VALID_RESPONSE = {
    "main_strength": "Strong academic record relative to this school's averages.",
    "main_risk": "Essay readiness is still early for this deadline.",
    "summary": "Overall a solid match based on your current profile.",
    "next_actions": ["Finish your primary essay draft", "Confirm your SAT score"],
}


@override_settings(AI_SEMANTIC_FIT_ENABLED=True, GEMINI_API_KEY="test-key")
class SemanticFitTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="fitcacheuser", email="fitcacheuser@test.com", password="testpass123"
        )
        self.profile, _ = ensure_profile_records(self.user)
        self.university = create_university("semantic-fit-university")
        self.client.force_authenticate(self.user)

    def _fit_url(self):
        return f"/api/v1/universities/{self.university.slug}/fit/"

    def _refresh_url(self):
        return f"/api/v1/universities/{self.university.slug}/fit/refresh/"

    def test_map_tier_uses_reach_competitive_target_safer_unknown_only(self):
        self.assertEqual(map_tier(None), "unknown")
        self.assertEqual(map_tier("reach"), "reach")
        self.assertEqual(map_tier("competitive"), "competitive")
        self.assertEqual(map_tier("target"), "target")
        self.assertEqual(map_tier("safety"), "safer")

    def test_university_list_never_touches_semantic_fit_client(self):
        with patch(
            "services.university_service.semantic_fit.GeminiSemanticFitClient"
        ) as client_cls:
            response = self.client.get("/api/v1/universities/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            client_cls.assert_not_called()

    def test_get_fit_never_calls_ai_when_cache_missing(self):
        with patch(
            "services.university_service.semantic_fit.GeminiSemanticFitClient"
        ) as client_cls:
            response = self.client.get(self._fit_url())
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            client_cls.assert_not_called()
        self.assertEqual(response.data["semantic_fit_status"], "missing")
        self.assertIsNone(response.data["semantic_fit"])
        self.assertIn("deterministic_fit", response.data)
        self.assertIn("tier", response.data)
        # Backward-compatible flat fields (existing FitAnalysisTests) stay present.
        self.assertIn("category", response.data)
        self.assertIn("fit_score", response.data)

    def test_get_fit_never_calls_ai_even_when_cache_exists(self):
        fake_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
        refresh_semantic_fit(self.user, self.university, client=fake_client)
        self.assertEqual(fake_client.calls, 1)

        with patch(
            "services.university_service.semantic_fit.GeminiSemanticFitClient"
        ) as client_cls:
            response = self.client.get(self._fit_url())
            client_cls.assert_not_called()
        self.assertEqual(response.data["semantic_fit_status"], "cached")
        self.assertEqual(response.data["semantic_fit"]["main_strength"], VALID_RESPONSE["main_strength"])
        self.assertEqual(response.data["main_strength"], VALID_RESPONSE["main_strength"])
        self.assertIsNotNone(response.data["last_updated"])

    def test_refresh_calls_ai_only_from_explicit_endpoint(self):
        fake_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
        with patch(
            "services.university_service.semantic_fit.GeminiSemanticFitClient",
            return_value=fake_client,
        ):
            response = self.client.post(self._refresh_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(fake_client.calls, 1)
        self.assertEqual(response.data["refresh_reason"], "refreshed")
        self.assertEqual(response.data["semantic_fit_status"], "cached")

    def test_refresh_is_a_no_op_when_valid_cache_already_exists(self):
        fake_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
        result = refresh_semantic_fit(self.user, self.university, client=fake_client)
        self.assertEqual(result["reason"], "refreshed")

        second_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
        second_result = refresh_semantic_fit(self.user, self.university, client=second_client)
        self.assertEqual(second_result["reason"], "cached")
        self.assertEqual(second_client.calls, 0)

    def test_cache_invalidates_when_profile_hash_changes(self):
        fake_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
        refresh_semantic_fit(self.user, self.university, client=fake_client)
        status_value, _record = semantic_fit_status(self.user, self.university)
        self.assertEqual(status_value, "cached")

        self.profile.gpa = "3.90"
        self.profile.gpa_scale = "4.00"
        self.profile.save()

        status_value_after, record_after = semantic_fit_status(self.user, self.university)
        self.assertEqual(status_value_after, "missing")
        self.assertIsNone(record_after)
        # The row itself is still there, just no longer considered valid --
        # confirms staleness is judged at read time, not by deleting data.
        self.assertTrue(
            UniversitySemanticFit.objects.filter(user=self.user, university=self.university).exists()
        )

    def test_cache_invalidates_when_university_updated_at_changes(self):
        fake_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
        refresh_semantic_fit(self.user, self.university, client=fake_client)
        status_value, _record = semantic_fit_status(self.user, self.university)
        self.assertEqual(status_value, "cached")

        self.university.summary = "Updated summary text."
        self.university.save(update_fields=["summary", "updated_at"])

        status_value_after, record_after = semantic_fit_status(self.user, self.university)
        self.assertEqual(status_value_after, "missing")
        self.assertIsNone(record_after)

    def test_ai_failure_does_not_break_deterministic_fit(self):
        fake_client = FakeSemanticFitClient(error=AIProviderError("boom"))
        with patch(
            "services.university_service.semantic_fit.GeminiSemanticFitClient",
            return_value=fake_client,
        ):
            response = self.client.post(self._refresh_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["refresh_reason"], "ai_unavailable")
        self.assertIn("deterministic_fit", response.data)
        self.assertIsNotNone(response.data["fit_score"])
        self.assertEqual(response.data["semantic_fit_status"], "failed")

    def test_ai_provider_unavailable_is_handled_like_any_other_failure(self):
        fake_client = FakeSemanticFitClient(error=AIProviderUnavailable("no key"))
        result = refresh_semantic_fit(self.user, self.university, client=fake_client)
        self.assertEqual(result["reason"], "ai_unavailable")

    def test_invalid_json_repairs_on_retry(self):
        fake_client = FakeSemanticFitClient(
            responses=[{"main_strength": "only one field"}, VALID_RESPONSE]
        )
        result = refresh_semantic_fit(self.user, self.university, client=fake_client)
        self.assertEqual(result["reason"], "refreshed")
        self.assertEqual(fake_client.calls, 2)

    def test_invalid_json_twice_stores_failed_status_without_raising(self):
        fake_client = FakeSemanticFitClient(
            responses=[{"main_strength": "bad"}, {"main_strength": "still bad"}]
        )
        result = refresh_semantic_fit(self.user, self.university, client=fake_client)
        self.assertEqual(result["reason"], "validation_failed")
        self.assertEqual(fake_client.calls, 2)
        status_value, record = semantic_fit_status(self.user, self.university)
        self.assertEqual(status_value, "failed")
        self.assertEqual(record.status, UniversitySemanticFit.Status.FAILED)

    def test_response_rejected_when_it_names_a_percentage_or_guarantee(self):
        fake_client = FakeSemanticFitClient(
            responses=[
                {**VALID_RESPONSE, "summary": "You have an 85% chance of admission."},
                VALID_RESPONSE,
            ]
        )
        result = refresh_semantic_fit(self.user, self.university, client=fake_client)
        # First response rejected by the forbidden-token check, repaired on retry.
        self.assertEqual(result["reason"], "refreshed")
        self.assertEqual(fake_client.calls, 2)

    def test_daily_limit_blocks_further_refreshes(self):
        with override_settings(AI_SEMANTIC_FIT_DAILY_LIMIT=1):
            first_university = create_university("semantic-fit-university-a")
            second_university = create_university("semantic-fit-university-b")
            client_a = FakeSemanticFitClient(responses=[VALID_RESPONSE])
            result_a = refresh_semantic_fit(self.user, first_university, client=client_a)
            self.assertEqual(result_a["reason"], "refreshed")

            client_b = FakeSemanticFitClient(responses=[VALID_RESPONSE])
            result_b = refresh_semantic_fit(self.user, second_university, client=client_b)
            self.assertEqual(result_b["reason"], "daily_limit_reached")
            self.assertEqual(client_b.calls, 0)

    def test_ai_unavailable_when_flag_disabled(self):
        with override_settings(AI_SEMANTIC_FIT_ENABLED=False):
            fake_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
            result = refresh_semantic_fit(self.user, self.university, client=fake_client)
        self.assertEqual(result["reason"], "ai_unavailable")
        self.assertEqual(fake_client.calls, 0)

    def test_get_fit_query_count_stays_bounded(self):
        fake_client = FakeSemanticFitClient(responses=[VALID_RESPONSE])
        refresh_semantic_fit(self.user, self.university, client=fake_client)

        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(self._fit_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(
            len(captured),
            45,
            "GET .../fit/ query count regressed -- check for a new N+1 in the deterministic "
            "fit calculation or the semantic-fit cache lookup.",
        )

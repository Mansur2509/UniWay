import json
import urllib.error
from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from services.ai_gateway_service.essay_scoring_client import GeminiEssayScoringClient
from services.ai_gateway_service.exceptions import AIProviderError, parse_gemini_error_body
from services.ai_gateway_service.gemini_client import GeminiProfileAssessmentClient


class _FakeResponse:
    def __init__(self, data: bytes):
        self._data = data

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _http_error(code: int, body: bytes, msg: str = "Error") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://generativelanguage.googleapis.com/v1beta/models/x:generateContent",
        code=code,
        msg=msg,
        hdrs=None,
        fp=BytesIO(body),
    )


def _gemini_error_body(code: int, status: str, message: str = "provider error") -> bytes:
    return json.dumps({"error": {"code": code, "message": message, "status": status}}).encode("utf-8")


class ParseGeminiErrorBodyTests(SimpleTestCase):
    def test_parses_well_formed_error_shape(self):
        code, status = parse_gemini_error_body(_gemini_error_body(404, "NOT_FOUND").decode())
        self.assertEqual(code, 404)
        self.assertEqual(status, "NOT_FOUND")

    def test_returns_none_none_for_non_json_body(self):
        self.assertEqual(parse_gemini_error_body("not json at all"), (None, None))

    def test_returns_none_none_for_json_without_error_key(self):
        self.assertEqual(parse_gemini_error_body(json.dumps({"foo": "bar"})), (None, None))

    def test_returns_none_none_for_non_object_json(self):
        self.assertEqual(parse_gemini_error_body(json.dumps([1, 2, 3])), (None, None))


@override_settings(GEMINI_API_KEY="test-key")
class GeminiEssayScoringClientDiagnosticsTests(SimpleTestCase):
    def _client(self):
        return GeminiEssayScoringClient(api_key="test-key", model_name="gemini-2.5-flash")

    def _score(self):
        return self._client().score_essay(system_prompt="s", user_prompt="u")

    def test_http_404_captures_status_body_and_provider_fields(self):
        body = _gemini_error_body(404, "NOT_FOUND", "models/x is not found for API version v1beta")
        with patch("urllib.request.urlopen", side_effect=_http_error(404, body)):
            with self.assertRaises(AIProviderError) as ctx:
                self._score()
        error = ctx.exception
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.cause_class, "HTTPError")
        self.assertEqual(error.provider_code, 404)
        self.assertEqual(error.provider_status, "NOT_FOUND")
        self.assertIn("NOT_FOUND", error.error_body)

    def test_http_400_403_429_are_all_captured_with_status_and_body(self):
        cases = [(400, "INVALID_ARGUMENT"), (403, "PERMISSION_DENIED"), (429, "RESOURCE_EXHAUSTED")]
        for code, provider_status in cases:
            body = _gemini_error_body(code, provider_status)
            with patch("urllib.request.urlopen", side_effect=_http_error(code, body)):
                with self.assertRaises(AIProviderError) as ctx:
                    self._score()
            self.assertEqual(ctx.exception.status_code, code)
            self.assertEqual(ctx.exception.provider_status, provider_status)
            self.assertTrue(ctx.exception.error_body)

    def test_timeout_produces_non_empty_sanitized_error(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            with self.assertRaises(AIProviderError) as ctx:
                self._score()
        error = ctx.exception
        self.assertIsNone(error.status_code)
        self.assertEqual(error.cause_class, "TimeoutError")
        self.assertTrue(error.error_body)

    def test_url_error_produces_non_empty_sanitized_error(self):
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
            with self.assertRaises(AIProviderError) as ctx:
                self._score()
        error = ctx.exception
        self.assertIsNone(error.status_code)
        self.assertEqual(error.cause_class, "URLError")
        self.assertIn("connection refused", error.error_body)

    def test_invalid_outer_json_produces_non_empty_sanitized_error(self):
        with patch("urllib.request.urlopen", return_value=_FakeResponse(b"not json")):
            with self.assertRaises(AIProviderError) as ctx:
                self._score()
        error = ctx.exception
        self.assertIsNone(error.status_code)
        self.assertEqual(error.cause_class, "JSONDecodeError")
        self.assertTrue(error.error_body)

    def test_response_missing_candidates_produces_non_empty_sanitized_error_via_message_fallback(self):
        ok_body = json.dumps({"candidates": []}).encode("utf-8")
        with patch("urllib.request.urlopen", return_value=_FakeResponse(ok_body)):
            with self.assertRaises(AIProviderError) as ctx:
                self._score()
        error = ctx.exception
        self.assertIsNone(error.status_code)
        self.assertEqual(str(error), "Gemini response did not include candidates.")
        self.assertEqual(error.error_body, "Gemini response did not include candidates.")

    def test_response_with_non_json_inner_text_produces_non_empty_sanitized_error(self):
        ok_body = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "not valid json"}]}}]}
        ).encode("utf-8")
        with patch("urllib.request.urlopen", return_value=_FakeResponse(ok_body)):
            with self.assertRaises(AIProviderError) as ctx:
                self._score()
        error = ctx.exception
        self.assertEqual(error.cause_class, "JSONDecodeError")
        self.assertTrue(error.error_body)


@override_settings(GEMINI_API_KEY="test-key")
class GeminiProfileAssessmentClientDiagnosticsTests(SimpleTestCase):
    def _client(self):
        return GeminiProfileAssessmentClient(api_key="test-key", model_name="gemini-2.5-flash")

    def test_http_error_captures_status_body_and_provider_fields(self):
        body = _gemini_error_body(404, "NOT_FOUND", "models/x is not found")
        with patch("urllib.request.urlopen", side_effect=_http_error(404, body)):
            with self.assertRaises(AIProviderError) as ctx:
                self._client().generate_profile_assessment({"foo": "bar"})
        error = ctx.exception
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.provider_status, "NOT_FOUND")
        self.assertEqual(error.cause_class, "HTTPError")

    def test_timeout_produces_non_empty_sanitized_error(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            with self.assertRaises(AIProviderError) as ctx:
                self._client().generate_profile_assessment({"foo": "bar"})
        error = ctx.exception
        self.assertIsNone(error.status_code)
        self.assertEqual(error.cause_class, "TimeoutError")
        self.assertTrue(error.error_body)

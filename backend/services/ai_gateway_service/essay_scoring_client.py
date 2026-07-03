from __future__ import annotations

import json
import urllib.error
import urllib.request

from django.conf import settings

from .exceptions import AIProviderError, AIProviderUnavailable


class GeminiEssayScoringClient:
    """Thin, backend-only Gemini client for essay scoring.

    Mirrors the request/response handling in `gemini_client.GeminiProfileAssessmentClient`
    (same provider, same urllib-based call, same error wrapping) but is parameterized by
    a plain system + user prompt pair instead of a profile-assessment-specific envelope,
    since essay scoring uses its own fixed system prompt and templated content built in
    `essay_service.ai_scoring`. Kept in this app (not essay_service) so all outbound AI
    provider calls stay in one place, per the backend-only AI gateway policy.
    """

    provider_name = "gemini"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model_name or settings.AI_ESSAY_MODEL
        self.timeout_seconds = timeout_seconds or settings.AI_ESSAY_TIMEOUT_SECONDS
        self.max_output_tokens = max_output_tokens or settings.AI_ESSAY_MAX_OUTPUT_TOKENS
        self.temperature = settings.AI_ESSAY_TEMPERATURE if temperature is None else temperature

    def score_essay(self, *, system_prompt: str, user_prompt: str) -> dict:
        if not self.api_key:
            raise AIProviderUnavailable("Gemini API key is not configured.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_output_tokens,
                "responseMimeType": "application/json",
            },
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            try:
                body = error.read().decode("utf-8", errors="replace")
            except Exception:
                body = ""
            raise AIProviderError(
                "Gemini essay scoring request failed.", status_code=error.code, error_body=body
            ) from error
        except (TimeoutError, urllib.error.URLError, json.JSONDecodeError) as error:
            raise AIProviderError("Gemini essay scoring request failed.") from error

        text = self._extract_text(data)
        try:
            return json.loads(text)
        except json.JSONDecodeError as error:
            raise AIProviderError("Gemini returned non-JSON essay scoring output.") from error

    @staticmethod
    def _extract_text(data: dict) -> str:
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise AIProviderError("Gemini response did not include candidates.")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not isinstance(parts, list) or not parts:
            raise AIProviderError("Gemini response did not include content parts.")
        text = parts[0].get("text", "")
        if not isinstance(text, str) or not text.strip():
            raise AIProviderError("Gemini response text was empty.")
        return text

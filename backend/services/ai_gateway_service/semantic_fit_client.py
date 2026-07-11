from __future__ import annotations

import json
import urllib.error
import urllib.request

from django.conf import settings

from .exceptions import AIProviderError, AIProviderUnavailable, parse_gemini_error_body
from .json_extraction import parse_json_response


class GeminiSemanticFitClient:
    """Thin, backend-only Gemini client for semantic university fit.

    Mirrors `essay_scoring_client.GeminiEssayScoringClient` (same provider,
    same urllib-based call, same error wrapping, same plain system/user
    prompt shape) -- kept as its own class per the established one-client-
    per-feature convention so quota/model/timeout tuning never collides with
    the other two AI features.
    """

    provider_name = "gemini"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: int | None = None,
        max_output_tokens: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model_name or settings.AI_SEMANTIC_FIT_MODEL
        self.timeout_seconds = timeout_seconds or settings.AI_SEMANTIC_FIT_TIMEOUT_SECONDS
        self.max_output_tokens = max_output_tokens or settings.AI_SEMANTIC_FIT_MAX_OUTPUT_TOKENS

    def generate_semantic_fit(
        self, *, system_prompt: str, user_prompt: str, response_schema: dict | None = None
    ) -> dict:
        if not self.api_key:
            raise AIProviderUnavailable("Gemini API key is not configured.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )
        generation_config = {
            "temperature": 0.3,
            "maxOutputTokens": self.max_output_tokens,
            "responseMimeType": "application/json",
        }
        if response_schema is not None:
            generation_config["responseSchema"] = response_schema
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": generation_config,
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
            provider_code, provider_status = parse_gemini_error_body(body)
            raise AIProviderError(
                "Gemini semantic fit request failed.",
                status_code=error.code,
                error_body=body,
                cause_class=type(error).__name__,
                provider_code=provider_code,
                provider_status=provider_status,
            ) from error
        except TimeoutError as error:
            raise AIProviderError(
                "Gemini semantic fit request timed out.",
                error_body="timeout while calling Gemini",
                cause_class=type(error).__name__,
            ) from error
        except urllib.error.URLError as error:
            raise AIProviderError(
                "Gemini semantic fit request failed.",
                error_body=f"network error contacting Gemini: {error.reason}",
                cause_class=type(error).__name__,
            ) from error
        except json.JSONDecodeError as error:
            raise AIProviderError(
                "Gemini returned an invalid JSON response.",
                error_body=f"invalid Gemini JSON response: {error}",
                cause_class=type(error).__name__,
            ) from error

        text = self._extract_text(data)
        try:
            return parse_json_response(text)
        except json.JSONDecodeError as error:
            raise AIProviderError(
                "Gemini returned non-JSON semantic fit output.",
                error_body=f"json decode failed: {error.msg} at pos {error.pos}",
                cause_class=type(error).__name__,
            ) from error

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

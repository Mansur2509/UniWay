import json


class AIProviderError(Exception):
    """Raised when a backend-only AI provider request fails safely.

    Carries only enough structured, sanitized detail (HTTP status code, a
    truncated provider error body, the wrapped exception's class name, and
    Gemini's own error `code`/`status` fields when parseable) for callers to
    log a diagnosable warning -- never the API key, the prompt, or any user
    content. `error_body` falls back to `message` when no separate provider
    body exists, so every raise site produces a non-empty, greppable log line.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_body: str = "",
        cause_class: str | None = None,
        provider_code: int | None = None,
        provider_status: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_body = (error_body or message or "")[:1000]
        self.cause_class = cause_class
        self.provider_code = provider_code
        self.provider_status = provider_status


class AIProviderUnavailable(AIProviderError):
    """Raised when provider configuration is missing or disabled."""


def parse_gemini_error_body(body: str) -> tuple[int | None, str | None]:
    """Best-effort parse of Gemini's `{"error": {"code", "status"}}` shape.

    Returns `(None, None)` for anything that doesn't match -- never raises,
    since this only runs while already handling a provider error.
    """

    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return None, None
    if not isinstance(parsed, dict):
        return None, None
    error = parsed.get("error")
    if not isinstance(error, dict):
        return None, None
    return error.get("code"), error.get("status")

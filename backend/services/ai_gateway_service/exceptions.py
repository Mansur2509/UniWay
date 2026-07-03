class AIProviderError(Exception):
    """Raised when a backend-only AI provider request fails safely.

    Carries only enough structured, sanitized detail (HTTP status code and a
    truncated provider error body) for callers to log a diagnosable warning --
    never the API key, the prompt, or any user content.
    """

    def __init__(self, message: str, *, status_code: int | None = None, error_body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_body = error_body[:1000]


class AIProviderUnavailable(AIProviderError):
    """Raised when provider configuration is missing or disabled."""

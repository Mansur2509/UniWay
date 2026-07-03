class AIProviderError(Exception):
    """Raised when a backend-only AI provider request fails safely."""


class AIProviderUnavailable(AIProviderError):
    """Raised when provider configuration is missing or disabled."""

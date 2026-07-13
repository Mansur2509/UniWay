import logging
import time

from django.conf import settings
from django.utils.cache import patch_vary_headers

logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
    """Logs every request's duration; WARNING-level when it exceeds
    `settings.SLOW_REQUEST_THRESHOLD_MS`, so a slow endpoint (N+1 query,
    missing cache, external call) shows up in production logs the same way
    the AI call paths already log their own duration_ms.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - started_at) * 1000)

        log_level = logging.WARNING if duration_ms >= settings.SLOW_REQUEST_THRESHOLD_MS else logging.DEBUG
        logger.log(
            log_level,
            "HTTP request method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response


class PrivateApiCacheControlMiddleware:
    """Prevent authenticated and state-changing API responses being cached.

    JWT authentication happens inside DRF rather than Django middleware, so
    the Authorization header is also treated as a private-response signal.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith("/api/"):
            return response

        user = getattr(request, "user", None)
        is_private = bool(
            request.method not in {"GET", "HEAD", "OPTIONS"}
            or request.path.startswith("/api/auth/")
            or request.headers.get("Authorization")
            or (user and user.is_authenticated)
        )
        if is_private:
            response["Cache-Control"] = "private, no-store"
            response["Pragma"] = "no-cache"
            patch_vary_headers(response, ("Authorization", "Cookie"))
        return response

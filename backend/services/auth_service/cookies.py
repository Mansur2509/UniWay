from __future__ import annotations

from django.conf import settings
from rest_framework.exceptions import PermissionDenied


def set_refresh_cookie(response, refresh_token: str) -> None:
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
    )


def clear_refresh_cookie(response) -> None:
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )


def refresh_token_from_request(request) -> str | None:
    cookie_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if cookie_token:
        validate_ambient_cookie_origin(request)
        return cookie_token

    # Transitional compatibility for sessions issued before the HttpOnly
    # cookie migration. New login/register/refresh responses never expose a
    # refresh token to JavaScript.
    body_token = request.data.get("refresh") if isinstance(request.data, dict) else None
    return body_token if isinstance(body_token, str) and body_token else None


def validate_ambient_cookie_origin(request) -> None:
    origin = (request.headers.get("Origin") or "").rstrip("/")
    if not origin:
        if request.headers.get("Sec-Fetch-Site") == "cross-site":
            raise PermissionDenied("Cross-site credential request rejected.")
        return

    allowed_origins = {
        value.rstrip("/")
        for value in (*settings.CORS_ALLOWED_ORIGINS, *settings.CSRF_TRUSTED_ORIGINS)
    }
    if origin not in allowed_origins:
        raise PermissionDenied("Cross-site credential request rejected.")

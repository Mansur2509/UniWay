from __future__ import annotations

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import urlencode, urlparse

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.db import IntegrityError, transaction
from django.utils import timezone
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token as google_id_token

from services.subscription_service.models import Plan, Subscription
from services.user_profile_service.models import StudentProfile, UserPreference

from .models import OAuthLoginAttempt, SocialIdentity

User = get_user_model()

GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"  # nosec B105 - public endpoint
GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
OAUTH_COOKIE_SALT = "uniway.google-oauth-attempt.v1"


class GoogleOAuthError(Exception):
    code = "failed"


class GoogleOAuthConfigurationError(GoogleOAuthError):
    code = "unavailable"


class GoogleOAuthValidationError(GoogleOAuthError):
    code = "invalid"


class GoogleOAuthAccountConflict(GoogleOAuthError):
    code = "conflict"


class GoogleOAuthAccountBlocked(GoogleOAuthError):
    code = "blocked"


@dataclass(frozen=True)
class GoogleOAuthAttempt:
    state: str
    nonce: str
    code_verifier: str


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _configured_frontend_url() -> str:
    target = settings.GOOGLE_OAUTH_FRONTEND_URL
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise GoogleOAuthConfigurationError
    origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    allowed = {value.rstrip("/") for value in settings.CORS_ALLOWED_ORIGINS}
    if origin not in allowed:
        raise GoogleOAuthConfigurationError
    if not settings.DEBUG and parsed.scheme != "https":
        raise GoogleOAuthConfigurationError
    return target


def oauth_frontend_redirect(code: str) -> str:
    target = _configured_frontend_url()
    separator = "&" if "?" in target else "?"
    return f"{target}{separator}{urlencode({'oauth': code})}"


def require_google_oauth_configuration() -> None:
    if not settings.GOOGLE_OAUTH_ENABLED:
        raise GoogleOAuthConfigurationError
    _configured_frontend_url()
    parsed_redirect = urlparse(settings.GOOGLE_REDIRECT_URI)
    if parsed_redirect.scheme not in {"http", "https"} or not parsed_redirect.netloc:
        raise GoogleOAuthConfigurationError
    if not settings.DEBUG and parsed_redirect.scheme != "https":
        raise GoogleOAuthConfigurationError


def create_google_oauth_attempt() -> tuple[GoogleOAuthAttempt, str]:
    require_google_oauth_configuration()
    attempt = GoogleOAuthAttempt(
        state=secrets.token_urlsafe(32),
        nonce=secrets.token_urlsafe(32),
        code_verifier=secrets.token_urlsafe(64),
    )
    OAuthLoginAttempt.objects.create(
        state_digest=_digest(attempt.state),
        nonce_digest=_digest(attempt.nonce),
        expires_at=timezone.now()
        + timedelta(seconds=settings.GOOGLE_OAUTH_ATTEMPT_MAX_AGE_SECONDS),
    )
    payload = signing.dumps(
        {
            "state": attempt.state,
            "nonce": attempt.nonce,
            "code_verifier": attempt.code_verifier,
        },
        salt=OAUTH_COOKIE_SALT,
        compress=True,
    )
    return attempt, payload


def build_google_authorization_url(attempt: GoogleOAuthAttempt) -> str:
    query = urlencode(
        {
            "response_type": "code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "state": attempt.state,
            "nonce": attempt.nonce,
            "code_challenge": _pkce_challenge(attempt.code_verifier),
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }
    )
    return f"{GOOGLE_AUTHORIZATION_ENDPOINT}?{query}"


def load_google_oauth_attempt(cookie_value: str | None, returned_state: str) -> GoogleOAuthAttempt:
    if not cookie_value or not returned_state:
        raise GoogleOAuthValidationError
    try:
        payload = signing.loads(
            cookie_value,
            salt=OAUTH_COOKIE_SALT,
            max_age=settings.GOOGLE_OAUTH_ATTEMPT_MAX_AGE_SECONDS,
        )
    except signing.BadSignature as error:
        raise GoogleOAuthValidationError from error
    try:
        attempt = GoogleOAuthAttempt(
            state=str(payload["state"]),
            nonce=str(payload["nonce"]),
            code_verifier=str(payload["code_verifier"]),
        )
    except (KeyError, TypeError) as error:
        raise GoogleOAuthValidationError from error
    if not secrets.compare_digest(attempt.state, returned_state):
        raise GoogleOAuthValidationError
    return attempt


@transaction.atomic
def consume_google_oauth_attempt(attempt: GoogleOAuthAttempt) -> None:
    try:
        stored = OAuthLoginAttempt.objects.select_for_update().get(
            state_digest=_digest(attempt.state),
            nonce_digest=_digest(attempt.nonce),
        )
    except OAuthLoginAttempt.DoesNotExist as error:
        raise GoogleOAuthValidationError from error
    now = timezone.now()
    if stored.consumed_at is not None or stored.expires_at <= now:
        raise GoogleOAuthValidationError
    stored.consumed_at = now
    stored.save(update_fields=("consumed_at",))


def exchange_google_code(code: str, code_verifier: str) -> str:
    if not code or len(code) > 4096:
        raise GoogleOAuthValidationError
    try:
        response = httpx.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "code_verifier": code_verifier,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise GoogleOAuthValidationError from error
    token = payload.get("id_token") if isinstance(payload, dict) else None
    if not isinstance(token, str) or not token:
        raise GoogleOAuthValidationError
    return token


def verify_google_id_token(token: str) -> dict:
    try:
        claims = google_id_token.verify_oauth2_token(
            token,
            GoogleAuthRequest(),
            settings.GOOGLE_CLIENT_ID,
        )
    except (GoogleAuthError, ValueError) as error:
        raise GoogleOAuthValidationError from error
    if not isinstance(claims, dict):
        raise GoogleOAuthValidationError
    return claims


def validate_google_claims(claims: dict, expected_nonce: str) -> dict[str, str]:
    issuer = claims.get("iss")
    audience = claims.get("aud")
    subject = claims.get("sub")
    email = claims.get("email")
    nonce = claims.get("nonce")
    expires_at = claims.get("exp")
    if issuer not in GOOGLE_ISSUERS or audience != settings.GOOGLE_CLIENT_ID:
        raise GoogleOAuthValidationError
    if not isinstance(expires_at, int | float) or expires_at <= time.time():
        raise GoogleOAuthValidationError
    if not isinstance(nonce, str) or not secrets.compare_digest(nonce, expected_nonce):
        raise GoogleOAuthValidationError
    if not isinstance(subject, str) or not subject or len(subject) > 255:
        raise GoogleOAuthValidationError
    if claims.get("email_verified") is not True or not isinstance(email, str) or not email:
        raise GoogleOAuthValidationError
    normalized_email = User.objects.normalize_email(email).lower()
    if len(normalized_email) > 254:
        raise GoogleOAuthValidationError
    name = claims.get("name")
    return {
        "subject": subject,
        "email": normalized_email,
        "name": name.strip()[:180] if isinstance(name, str) else "",
    }


@transaction.atomic
def get_or_link_google_user(identity_data: dict[str, str]):
    subject = identity_data["subject"]
    email = identity_data["email"]
    identity = (
        SocialIdentity.objects.select_for_update()
        .select_related("user")
        .filter(provider=SocialIdentity.Provider.GOOGLE, subject=subject)
        .first()
    )
    if identity is not None:
        user = identity.user
        if not user.is_active:
            raise GoogleOAuthAccountBlocked
        identity.email_at_link = email
        identity.save(update_fields=("email_at_link", "last_login_at"))
        return user

    user = User.objects.select_for_update().filter(email__iexact=email).first()
    if user is not None:
        if not user.is_active:
            raise GoogleOAuthAccountBlocked
        if user.role != User.Role.STUDENT or user.is_staff or user.is_superuser:
            raise GoogleOAuthAccountConflict
    else:
        try:
            user = User(username=email, email=email, role=User.Role.STUDENT)
            user.set_unusable_password()
            user.save()
        except IntegrityError as error:
            user = User.objects.select_for_update().filter(email__iexact=email).first()
            if user is None:
                raise GoogleOAuthAccountConflict from error
            if not user.is_active:
                raise GoogleOAuthAccountBlocked from error
            if user.role != User.Role.STUDENT or user.is_staff or user.is_superuser:
                raise GoogleOAuthAccountConflict from error

    try:
        SocialIdentity.objects.create(
            user=user,
            provider=SocialIdentity.Provider.GOOGLE,
            subject=subject,
            email_at_link=email,
        )
    except IntegrityError as error:
        existing = SocialIdentity.objects.select_related("user").filter(
            provider=SocialIdentity.Provider.GOOGLE,
            subject=subject,
        ).first()
        if existing is None or existing.user_id != user.id:
            raise GoogleOAuthAccountConflict from error

    profile, _ = StudentProfile.objects.get_or_create(user=user)
    if identity_data.get("name") and not profile.full_name:
        profile.full_name = identity_data["name"]
        profile.save(update_fields=("full_name", "updated_at"))
    UserPreference.objects.get_or_create(user=user)
    Subscription.objects.get_or_create(user=user, defaults={"plan": Plan.FREE})
    return user

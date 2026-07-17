import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from config.database_guard import validate_production_database
from config.deploy_guard import validate_deploy_config

BASE_DIR = Path(__file__).resolve().parent.parent


def csv_env(name: str, default: str = "") -> list[str]:
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-before-deploy")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = csv_env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "common",
    "services.auth_service",
    "services.user_profile_service",
    "services.university_service",
    "services.event_service",
    "services.roadmap_service",
    "services.essay_service",
    "services.application_service",
    "services.suggestions_service",
    "services.profile_assessment_service",
    "services.ai_gateway_service",
    "services.exam_content_service",
    "services.finance_literacy_service",
    "services.subscription_service",
    "services.notification_service",
    "services.research_service",
    "services.activity_service",
    "services.feedback_service",
    "services.telegram_service",
    "services.institution_service",
    "services.mentor_service",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.PrivateApiCacheControlMiddleware",
    "common.middleware.RequestTimingMiddleware",
]

SLOW_REQUEST_THRESHOLD_MS = int(os.getenv("SLOW_REQUEST_THRESHOLD_MS", "1000"))

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default="postgresql://uniway:change-me-for-local-development@localhost:5432/uniway",
        conn_max_age=60,
        conn_health_checks=True,
    )
}

# Fail loudly (ImproperlyConfigured) if production would start against a
# fallback/local database -- see config/database_guard.py for the rationale.
validate_production_database(
    debug=DEBUG,
    database_url=os.getenv("DATABASE_URL", ""),
    engine=DATABASES["default"]["ENGINE"],
)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "auth_service.User"

CORS_ALLOWED_ORIGINS = csv_env("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
CSRF_TRUSTED_ORIGINS = csv_env("CSRF_TRUSTED_ORIGINS", "http://localhost:3000")
CORS_ALLOW_CREDENTIALS = True

# Fail loudly (ImproperlyConfigured) on a malformed ALLOWED_HOSTS/CORS/CSRF
# value in production -- see config/deploy_guard.py for the rationale.
validate_deploy_config(
    debug=DEBUG,
    allowed_hosts=ALLOWED_HOSTS,
    cors_allowed_origins=CORS_ALLOWED_ORIGINS,
    csrf_trusted_origins=CSRF_TRUSTED_ORIGINS,
    secret_key=SECRET_KEY,
)

SECURE_COOKIES = os.getenv("DJANGO_SECURE_COOKIES", "false").lower() == "true"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = SECURE_COOKIES
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG and os.getenv("DJANGO_SECURE_SSL_REDIRECT", "true").lower() == "true"
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = False
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# The refresh credential is an ambient browser credential and is therefore
# never returned to frontend JavaScript. Production uses SameSite=None because
# the Vercel frontend and Render API are on different sites; Secure is required
# by browsers for that mode. Local HTTP development stays on Lax.
AUTH_REFRESH_COOKIE_NAME = os.getenv("AUTH_REFRESH_COOKIE_NAME", "uniway_refresh")
AUTH_REFRESH_COOKIE_PATH = os.getenv("AUTH_REFRESH_COOKIE_PATH", "/api/auth/")
AUTH_REFRESH_COOKIE_DOMAIN = os.getenv("AUTH_REFRESH_COOKIE_DOMAIN") or None
AUTH_REFRESH_COOKIE_SAMESITE = os.getenv(
    "AUTH_REFRESH_COOKIE_SAMESITE",
    "None" if SECURE_COOKIES else "Lax",
)
if AUTH_REFRESH_COOKIE_SAMESITE not in {"Lax", "Strict", "None"}:
    raise ImproperlyConfigured("AUTH_REFRESH_COOKIE_SAMESITE must be Lax, Strict, or None.")
if not DEBUG and (not SECURE_COOKIES or AUTH_REFRESH_COOKIE_SAMESITE != "None"):
    raise ImproperlyConfigured(
        "Production authentication requires DJANGO_SECURE_COOKIES=true and "
        "AUTH_REFRESH_COOKIE_SAMESITE=None for the cross-site frontend/API topology."
    )

# Backend-owned Google authorization-code flow. The client secret never enters
# a frontend environment, and the callback returns only to this fixed,
# allowlisted URL rather than a request-provided destination.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
GOOGLE_OAUTH_FRONTEND_URL = os.getenv(
    "GOOGLE_OAUTH_FRONTEND_URL",
    f"{CORS_ALLOWED_ORIGINS[0].rstrip('/')}/login" if CORS_ALLOWED_ORIGINS else "",
)
GOOGLE_OAUTH_STATE_COOKIE_NAME = os.getenv(
    "GOOGLE_OAUTH_STATE_COOKIE_NAME", "uniway_google_oauth"
)
GOOGLE_OAUTH_ATTEMPT_MAX_AGE_SECONDS = int(
    os.getenv("GOOGLE_OAUTH_ATTEMPT_MAX_AGE_SECONDS", "600")
)
GOOGLE_OAUTH_ENABLED = all(
    (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_OAUTH_FRONTEND_URL)
)

# Password reset email delivery. No credentials are hardcoded: real SMTP/API
# settings are provided only via environment variables in production. In
# DEBUG (local/dev), mail defaults to Django's console backend, which prints
# the reset email (including the link) to the server log instead of sending
# it -- no external provider is required to exercise the flow locally.
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "UniWay <no-reply@uniway.local>")
PASSWORD_RESET_FRONTEND_URL = os.getenv(
    "PASSWORD_RESET_FRONTEND_URL",
    f"{CORS_ALLOWED_ORIGINS[0].rstrip('/')}/reset-password" if CORS_ALLOWED_ORIGINS else "",
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "common.pagination.DefaultPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/hour",
        "user": "500/hour",
        "ai": "20/day",
        "ai_essay_score": "30/hour",
        "ai_fit_refresh": "30/hour",
        "auth_login": "10/hour",
        "auth_register": "5/hour",
        "auth_refresh": "30/hour",
        "auth_oauth": "30/hour",
        "password_reset_request": "5/hour",
        "password_reset_confirm": "10/hour",
        "feedback_submit": "10/hour",
        "report_submit": "20/hour",
        "organizer_application_submit": "5/hour",
        "event_registration": "30/hour",
        "event_submission": "60/hour",
        "event_moderation": "120/hour",
        "university_import": "20/hour",
        "telegram_link_token": "10/hour",
        "telegram_webhook": "120/minute",
        "telegram_mini_app_session": "30/hour",
        "billing_checkout": "20/hour",
        "billing_webhook": "120/minute",
        "billing_cancel": "10/hour",
    },
}
if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
    ]

# Beta-only fallback while no real background queue exists. Production should
# leave this false so admin uploads return immediately and process in a daemon
# thread instead of blocking gunicorn startup or the request path.
UNIVERSITY_IMPORT_RUN_INLINE = (
    os.getenv("UNIVERSITY_IMPORT_RUN_INLINE", "false").lower() == "true"
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_DEFAULT_MODEL", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Telegram Bot / Mini App foundation (POST-V1-021 Phase 5). Empty by default:
# every telegram_service endpoint checks TELEGRAM_BOT_TOKEN presence and
# returns a clear "not configured" response instead of attempting a live
# call when it is unset -- see services/telegram_service/services.py.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Billing/entitlement architecture (POST-V1-021 Phase 9). Sandbox-only: no
# live payment provider is integrated, so this secret signs/verifies only
# the sandbox webhook simulator, never a real provider delivery. Empty by
# default -- an unset secret means verify_webhook_signature() always fails
# closed (see services/subscription_service/billing.py).
BILLING_WEBHOOK_SECRET = os.getenv("BILLING_WEBHOOK_SECRET", "")
AI_PROFILE_ASSESSMENT_MODEL = os.getenv(
    "AI_PROFILE_ASSESSMENT_MODEL",
    "gemini-1.5-flash",
)
AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", "20"))
AI_MAX_OUTPUT_TOKENS = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "1200"))
AI_PROFILE_ASSESSMENT_ENABLED = (
    os.getenv("AI_PROFILE_ASSESSMENT_ENABLED", "false").lower() == "true"
)
AI_PROFILE_ASSESSMENT_DAILY_LIMIT = int(
    os.getenv("AI_PROFILE_ASSESSMENT_DAILY_LIMIT", "1")
)

# Essay scoring reuses GEMINI_API_KEY above; everything else is scoped to its
# own env vars so quota/model/timeout tuning never collides with profile
# assessment.
AI_ESSAY_SCORING_ENABLED = os.getenv("AI_ESSAY_SCORING_ENABLED", "false").lower() == "true"
AI_ESSAY_MODEL = os.getenv("AI_ESSAY_MODEL", "gemini-flash-latest")
AI_ESSAY_TIMEOUT_SECONDS = int(os.getenv("AI_ESSAY_TIMEOUT_SECONDS", "30"))
# Hard ceiling on the total wall-clock time `score_essay` may spend calling
# Gemini across up to 4 sequential attempts (initial + retry + validation-
# repair + repair-retry), each bounded by AI_ESSAY_TIMEOUT_SECONDS above. Left
# unbounded, that worst case is ~4*30s=120s -- longer than Gunicorn's own
# worker timeout in production (the Render dashboard's start command has no
# explicit --timeout, so Gunicorn's 30s default applies), which kills the
# worker mid-request before the app can return its own structured error
# response, and the client sees a raw, contentless 503 instead. This setting
# bounds the section to a safe fraction of that so a slow/flaky provider call
# degrades to a clean `ai_unavailable` response instead of an infra-level
# kill. Must stay comfortably below whatever Gunicorn --timeout is actually
# configured with in production (see backend/Dockerfile and
# docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md).
AI_ESSAY_REVIEW_MAX_WALL_SECONDS = int(os.getenv("AI_ESSAY_REVIEW_MAX_WALL_SECONDS", "80"))
# Short, fixed backoff before the single retry in each of the two possible
# retry pairs (initial-score retry, validation-repair retry) -- see
# ai_scoring.py's _call_gemini_with_retry. Deliberately small so it barely
# dents the AI_ESSAY_REVIEW_MAX_WALL_SECONDS budget above.
AI_ESSAY_RETRY_BACKOFF_SECONDS = float(os.getenv("AI_ESSAY_RETRY_BACKOFF_SECONDS", "1"))
AI_ESSAY_REPAIR_RETRY_BACKOFF_SECONDS = float(os.getenv("AI_ESSAY_REPAIR_RETRY_BACKOFF_SECONDS", "2"))
AI_ESSAY_MAX_OUTPUT_TOKENS = int(os.getenv("AI_ESSAY_MAX_OUTPUT_TOKENS", "2500"))
AI_ESSAY_TEMPERATURE = float(os.getenv("AI_ESSAY_TEMPERATURE", "0"))
AI_ESSAY_DAILY_FREE_LIMIT = int(os.getenv("AI_ESSAY_DAILY_FREE_LIMIT", "1"))
AI_ESSAY_BASIC_MONTHLY_LIMIT = int(os.getenv("AI_ESSAY_BASIC_MONTHLY_LIMIT", "10"))
AI_ESSAY_PREMIUM_MONTHLY_LIMIT = int(os.getenv("AI_ESSAY_PREMIUM_MONTHLY_LIMIT", "30"))
AI_ESSAY_PRO_MONTHLY_LIMIT = int(os.getenv("AI_ESSAY_PRO_MONTHLY_LIMIT", "100"))

# Semantic university fit (PERFORMANCE-011 PART 5-6) reuses GEMINI_API_KEY;
# scoped to its own env vars for the same reason essay scoring is. Never
# called on GET .../fit/ -- only from the explicit POST .../fit/refresh/
# action, and disabled by default like the other two AI features.
AI_SEMANTIC_FIT_ENABLED = os.getenv("AI_SEMANTIC_FIT_ENABLED", "false").lower() == "true"
AI_SEMANTIC_FIT_MODEL = os.getenv("AI_SEMANTIC_FIT_MODEL", "gemini-flash-latest")
AI_SEMANTIC_FIT_TIMEOUT_SECONDS = int(os.getenv("AI_SEMANTIC_FIT_TIMEOUT_SECONDS", "20"))
AI_SEMANTIC_FIT_MAX_OUTPUT_TOKENS = int(os.getenv("AI_SEMANTIC_FIT_MAX_OUTPUT_TOKENS", "600"))
AI_SEMANTIC_FIT_DAILY_LIMIT = int(os.getenv("AI_SEMANTIC_FIT_DAILY_LIMIT", "20"))

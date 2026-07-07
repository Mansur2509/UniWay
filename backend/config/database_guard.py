"""Startup guard: production must never run against a fallback database.

`settings.py` builds DATABASES via dj-database-url with a localhost-postgres
development default. In production (DJANGO_DEBUG=false) that default must
never be reached: a missing or mistyped DATABASE_URL would point the app at a
database that does not exist -- or, for a hypothetical sqlite URL, at a local
file that starts empty on every deploy -- and the symptom would be "all user
data disappeared" instead of an obvious deploy failure. Raising
ImproperlyConfigured at settings-import time turns silent misconfiguration
into a loud, immediate deploy error before gunicorn ever binds.
"""

from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured


def validate_production_database(*, debug: bool, database_url: str, engine: str) -> None:
    """Raise ImproperlyConfigured for unsafe production database configs.

    Local development (debug=True) is exempt so `runserver`/tests keep
    working against SQLite or a local Postgres without extra env vars.
    """

    if debug:
        return

    if not (database_url or "").strip():
        raise ImproperlyConfigured(
            "DATABASE_URL is not set while DJANGO_DEBUG=false. Refusing to fall back to the "
            "development default so production can never silently start against the wrong "
            "(or an empty) database. Set DATABASE_URL in the deployment environment."
        )

    if "sqlite" in (engine or "").lower():
        raise ImproperlyConfigured(
            "DATABASE_URL resolves to SQLite while DJANGO_DEBUG=false. A local file database "
            "in production starts empty on every deploy and loses data on restart; point "
            "DATABASE_URL at the managed Postgres database instead."
        )

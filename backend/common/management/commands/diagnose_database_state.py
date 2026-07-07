"""Read-only production database diagnostic.

Prints only sanitized connection facts (vendor, masked host and database
name, a detected Supabase project ref) plus table and row counts -- never the
password, the full DATABASE_URL, or any key/token. Safe to run against
production: it performs introspection and SELECT COUNT(*) queries only and
never writes.
"""

from __future__ import annotations

import os
import re
from importlib import import_module
from pathlib import PurePosixPath, PureWindowsPath

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

DEFAULT_TARGET_EMAIL = "timarus52111@gmail.com"

# (report label, module path, model class) for the user-owned data tables the
# data-loss audit cares about. Imported lazily and defensively so a renamed
# model degrades to a skipped line instead of crashing the diagnostic.
USER_DATA_MODEL_SPECS = (
    ("StudentProfile", "services.user_profile_service.models", "StudentProfile"),
    ("ApplicationTrackerItem", "services.application_service.models", "ApplicationTrackerItem"),
    ("EssayWorkspace", "services.essay_service.models", "EssayWorkspace"),
    ("SavedUniversity", "services.university_service.models", "SavedUniversity"),
    ("RoadmapTask", "services.roadmap_service.models", "RoadmapTask"),
)

USER_TABLE = "auth_service_user"


def sanitize_host(host: str) -> str:
    if not host:
        return "(empty -- localhost/development fallback)"
    if host in ("localhost", "127.0.0.1"):
        return host
    if "supabase" in host:
        # Keep only the provider suffix; the project ref is reported
        # separately so the operator can compare it with the dashboard.
        suffix = ".".join(host.split(".")[-2:])
        return f"****.{suffix}"
    if len(host) <= 8:
        return host[0] + "****"
    return host[:3] + "****" + host[-6:]


def sanitize_db_name(name: str, vendor: str) -> str:
    if not name:
        return "(empty)"
    if vendor == "sqlite":
        # A sqlite NAME is a filesystem path that can embed the OS username --
        # report only the file name itself.
        text = str(name)
        path = PureWindowsPath(text) if "\\" in text else PurePosixPath(text)
        return path.name
    if len(name) <= 10:
        return name
    return name[:4] + "****"


def detect_supabase_ref(host: str, user: str) -> str | None:
    match = re.search(r"db\.([a-z0-9]{16,32})\.supabase\.(?:co|com)", host or "")
    if match:
        return match.group(1)
    if "pooler.supabase" in (host or ""):
        # Pooler connections carry the ref in the username: "postgres.<ref>".
        match = re.fullmatch(r"[a-zA-Z0-9_]+\.([a-z0-9]{16,32})", user or "")
        if match:
            return match.group(1)
    return None


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if not domain:
        return "***"
    visible = local[:2] if len(local) > 2 else local[:1]
    return f"{visible}***@{domain}"


def user_data_tables() -> list[tuple[str, str]]:
    entries = []
    for label, module_path, attr in USER_DATA_MODEL_SPECS:
        try:
            model = getattr(import_module(module_path), attr)
        except (ImportError, AttributeError):
            continue
        entries.append((label, model._meta.db_table))
    return entries


class Command(BaseCommand):
    help = (
        "Read-only diagnostic: report (sanitized) which database this backend is "
        "connected to and whether Django tables and user data exist in it. "
        "Never prints secrets and never writes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=DEFAULT_TARGET_EMAIL,
            help="Account email to look for in the user table (default: the audit target).",
        )

    def handle(self, *args, **options):
        email = options["email"]
        settings_dict = connection.settings_dict
        host = settings_dict.get("HOST") or ""

        self.stdout.write(f"vendor: {connection.vendor}")
        self.stdout.write(f"engine: {settings_dict.get('ENGINE', '')}")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"DATABASE_URL env set: {bool(os.getenv('DATABASE_URL'))}")
        self.stdout.write(f"db host (sanitized): {sanitize_host(host)}")
        ref = detect_supabase_ref(host, settings_dict.get("USER") or "")
        self.stdout.write(f"supabase project ref: {ref or '(not detected)'}")
        self.stdout.write(
            f"db name (sanitized): {sanitize_db_name(settings_dict.get('NAME') or '', connection.vendor)}"
        )

        with connection.cursor() as cursor:
            tables = sorted(connection.introspection.table_names(cursor))
            table_set = set(tables)
            self.stdout.write(f"table count: {len(tables)}")
            for name in tables[:30]:
                self.stdout.write(f"  - {name}")
            if len(tables) > 30:
                self.stdout.write(f"  ... and {len(tables) - 30} more")

            self.stdout.write(f"django_migrations exists: {'django_migrations' in table_set}")
            self.stdout.write(f"{USER_TABLE} exists: {USER_TABLE in table_set}")

            quote = connection.ops.quote_name
            if USER_TABLE in table_set:
                cursor.execute(f"SELECT COUNT(*) FROM {quote(USER_TABLE)}")
                self.stdout.write(f"total users: {cursor.fetchone()[0]}")
                cursor.execute(
                    f"SELECT COUNT(*) FROM {quote(USER_TABLE)} WHERE LOWER(email) = LOWER(%s)",
                    [email],
                )
                found = cursor.fetchone()[0] > 0
                self.stdout.write(f"target email ({mask_email(email)}) found: {found}")

            for label, table in user_data_tables():
                if table in table_set:
                    cursor.execute(f"SELECT COUNT(*) FROM {quote(table)}")
                    self.stdout.write(f"{label} rows: {cursor.fetchone()[0]}")
                else:
                    self.stdout.write(f"{label} rows: (table {table} missing)")

        self.stdout.write(self.style.SUCCESS("Diagnostic complete -- no writes were performed."))

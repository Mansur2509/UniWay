"""No-op migration (kept for numbering only).

This migration originally ran the XLSX dataset import via RunPython during
`migrate`. On Render that blocked gunicorn from opening its port within the
deploy's port-scan window ("no open ports detected"), so the web deploy was
killed. A heavy data load must never run inside web-service startup.

The import logic has been removed and this is now an inert no-op so the deploy
can apply migrations quickly and start the server. Migration 0005 (the schema
columns) is unaffected. The dataset is loaded out-of-band instead — see
docs/DATA_SOURCES.md and the `import_universities_xlsx` management command.
"""

from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("university_service", "0005_university_ap_recommendations_and_more"),
    ]

    operations = []

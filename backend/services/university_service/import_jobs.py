from __future__ import annotations

import tempfile
import threading
from contextlib import suppress
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import close_old_connections, transaction
from django.utils import timezone

from .models import UniversityImportJob
from .xlsx_import import import_rows, load_xlsx_rows

MAX_IMPORT_UPLOAD_BYTES = 10 * 1024 * 1024


def save_uploaded_workbook(uploaded_file: UploadedFile) -> Path:
    suffix = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(
        delete=False,
        prefix="eduverse_university_import_",
        suffix=suffix or ".xlsx",
    ) as temporary:
        for chunk in uploaded_file.chunks():
            temporary.write(chunk)
        return Path(temporary.name)


def enqueue_university_import_job(
    *,
    uploaded_by,
    mode: str,
    uploaded_file: UploadedFile,
) -> UniversityImportJob:
    job = UniversityImportJob.objects.create(
        uploaded_by=uploaded_by,
        mode=mode,
        original_filename=Path(uploaded_file.name).name[:255],
    )
    workbook_path = save_uploaded_workbook(uploaded_file)

    if getattr(settings, "UNIVERSITY_IMPORT_RUN_INLINE", False):
        run_university_import_job(job.id, workbook_path)
        job.refresh_from_db()
        return job

    thread = threading.Thread(
        target=run_university_import_job,
        args=(job.id, workbook_path),
        name=f"university-import-job-{job.id}",
        daemon=True,
    )
    thread.start()
    return job


def run_university_import_job(job_id: int, workbook_path: str | Path) -> None:
    close_old_connections()
    path = Path(workbook_path)
    try:
        job = UniversityImportJob.objects.get(pk=job_id)
        job.status = UniversityImportJob.Status.RUNNING
        job.started_at = timezone.now()
        job.error_message = ""
        job.save(update_fields=("status", "started_at", "error_message"))

        rows = load_xlsx_rows(path)
        import_kwargs = {
            "replace_existing": False,
            "include_questionable": False,
            "source_label": f"Admin upload: {job.original_filename}",
            "default_verification": "partial",
        }
        if job.mode == UniversityImportJob.Mode.DRY_RUN:
            with transaction.atomic():
                report = import_rows(rows, **import_kwargs)
                transaction.set_rollback(True)
        else:
            with transaction.atomic():
                report = import_rows(rows, **import_kwargs)

        report_payload = report.as_dict()
        summary = report_payload["summary"]
        job.status = UniversityImportJob.Status.COMPLETED
        job.row_count = len(rows)
        job.created_count = summary["created"]
        job.updated_count = summary["updated"]
        job.skipped_count = summary["skipped"]
        job.warning_count = summary["warnings"]
        job.source_url_count = summary["source_urls"]
        job.field_verification_count = summary["fields_verified"]
        job.parsed_deadline_count = summary["parsed_deadlines"]
        job.parsed_essay_count = summary["parsed_essays"]
        job.questionable_sat_count = summary["placeholder_sat"]
        job.summary_json = report_payload
        job.finished_at = timezone.now()
        job.save(
            update_fields=(
                "status",
                "row_count",
                "created_count",
                "updated_count",
                "skipped_count",
                "warning_count",
                "source_url_count",
                "field_verification_count",
                "parsed_deadline_count",
                "parsed_essay_count",
                "questionable_sat_count",
                "summary_json",
                "finished_at",
            )
        )
    except Exception as exc:
        try:
            job = UniversityImportJob.objects.get(pk=job_id)
            job.status = UniversityImportJob.Status.FAILED
            job.error_message = str(exc)[:4000]
            job.finished_at = timezone.now()
            job.save(update_fields=("status", "error_message", "finished_at"))
        except UniversityImportJob.DoesNotExist:
            pass
    finally:
        with suppress(OSError):
            path.unlink(missing_ok=True)
        close_old_connections()

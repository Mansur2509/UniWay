from datetime import datetime, time

from django.db import migrations, models
from django.utils import timezone


def backfill_exam_date_metadata(apps, schema_editor):
    OfficialExamDate = apps.get_model("exam_content_service", "OfficialExamDate")
    for item in OfficialExamDate.objects.all().iterator():
        item.exam_year = item.test_date.year if item.test_date else None
        item.source_title = "College Board official exam schedule"
        if item.last_verified_date:
            item.last_verified_at = timezone.make_aware(
                datetime.combine(item.last_verified_date, time.min),
                timezone.get_current_timezone(),
            )
        item.local_timezone = "local testing time"
        item.save(
            update_fields=(
                "exam_year",
                "source_title",
                "last_verified_at",
                "local_timezone",
            )
        )


class Migration(migrations.Migration):
    dependencies = [
        ("exam_content_service", "0003_exam_date_metadata_and_2026_seed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="officialexamdate",
            name="test_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="officialexamdate",
            name="verification_status",
            field=models.CharField(
                choices=[
                    ("verified", "Verified"),
                    ("partial", "Partial"),
                    ("not_published", "Not published"),
                    ("outdated", "Outdated"),
                    ("requires_review", "Requires review"),
                ],
                default="partial",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="officialexamdate",
            name="exam_year",
            field=models.PositiveSmallIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="officialexamdate",
            name="last_verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="officialexamdate",
            name="local_timezone",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="officialexamdate",
            name="source_title",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.RunPython(backfill_exam_date_metadata, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="officialexamdate",
            options={"ordering": ("exam_year", "test_date", "exam_type")},
        ),
    ]

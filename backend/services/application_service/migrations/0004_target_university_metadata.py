from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("application_service", "0003_applicationtrackeritem_fit_tier_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationtrackeritem",
            name="archived_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationtrackeritem",
            name="personal_estimated_deadline",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationtrackeritem",
            name="target_intake_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.RemoveConstraint(
            model_name="applicationtrackeritem",
            name="unique_application_per_university",
        ),
        migrations.AddConstraint(
            model_name="applicationtrackeritem",
            constraint=models.UniqueConstraint(
                condition=Q(archived_at__isnull=True),
                fields=("user", "university"),
                name="unique_active_application_per_university",
            ),
        ),
        migrations.AddIndex(
            model_name="applicationtrackeritem",
            index=models.Index(
                fields=["user", "archived_at"],
                name="app_service_user_id_2e4444_idx",
            ),
        ),
    ]

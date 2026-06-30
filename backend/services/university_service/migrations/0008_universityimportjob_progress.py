from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("university_service", "0007_universityimportjob"),
    ]

    operations = [
        migrations.AddField(
            model_name="universityimportjob",
            name="processed_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="universityimportjob",
            name="current_row",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="universityimportjob",
            name="current_university",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="universityimportjob",
            name="last_heartbeat_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

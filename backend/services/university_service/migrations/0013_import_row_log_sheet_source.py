from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("university_service", "0012_university_data_import_fingerprints"),
    ]

    operations = [
        migrations.AddField(
            model_name="universitydataimportrowlog",
            name="source_row_number",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="universitydataimportrowlog",
            name="source_sheet_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddIndex(
            model_name="universitydataimportrowlog",
            index=models.Index(
                fields=["source_file_name", "source_sheet_name", "source_row_number"],
                name="university__source__4edf33_idx",
            ),
        ),
    ]

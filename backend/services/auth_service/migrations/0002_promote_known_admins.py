from django.db import migrations

ADMIN_EMAILS = (
    "timarus52111@gmail.com",
    "khamidjonovmansurjon@gmail.com",
    "iilich6304@gmail.com",
)


def promote_existing_admins(apps, schema_editor):
    user_model = apps.get_model("auth_service", "User")

    for email in ADMIN_EMAILS:
        users = list(user_model.objects.filter(email__iexact=email).order_by("id"))
        if len(users) != 1:
            continue

        user = users[0]
        if user.role == "admin" and user.is_staff:
            continue

        user.role = "admin"
        user.is_staff = True
        user.save(update_fields=["role", "is_staff"])


class Migration(migrations.Migration):
    dependencies = [
        ("auth_service", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(promote_existing_admins, migrations.RunPython.noop),
    ]

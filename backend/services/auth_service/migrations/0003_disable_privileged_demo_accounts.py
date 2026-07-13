from django.contrib.auth.hashers import make_password
from django.db import migrations

PRIVILEGED_DEMO_EMAILS = (
    "organizer.demo@eduverse.local",
    "admin.demo@eduverse.local",
    "organizer.demo@uniway.local",
    "admin.demo@uniway.local",
)


def disable_privileged_demo_accounts(apps, schema_editor):
    user_model = apps.get_model("auth_service", "User")
    unusable_password = make_password(None)
    for email in PRIVILEGED_DEMO_EMAILS:
        user_model.objects.filter(email__iexact=email).update(
            is_active=False,
            is_staff=False,
            is_superuser=False,
            password=unusable_password,
        )


class Migration(migrations.Migration):
    dependencies = [("auth_service", "0002_promote_known_admins")]

    operations = [
        migrations.RunPython(
            disable_privileged_demo_accounts,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

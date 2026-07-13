import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_service", "0003_disable_privileged_demo_accounts"),
    ]

    operations = [
        migrations.CreateModel(
            name="OAuthLoginAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("state_digest", models.CharField(max_length=64, unique=True)),
                ("nonce_digest", models.CharField(max_length=64)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="SocialIdentity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "provider",
                    models.CharField(choices=[("google", "Google")], max_length=20),
                ),
                ("subject", models.CharField(max_length=255)),
                ("email_at_link", models.EmailField(max_length=254)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_login_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="social_identities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="socialidentity",
            constraint=models.UniqueConstraint(
                fields=("provider", "subject"), name="unique_social_provider_subject"
            ),
        ),
        migrations.AddConstraint(
            model_name="socialidentity",
            constraint=models.UniqueConstraint(
                fields=("provider", "user"), name="unique_social_provider_user"
            ),
        ),
    ]

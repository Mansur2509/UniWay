from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        ORGANIZER = "organizer", "Organizer"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, db_index=True)

    @property
    def is_organizer(self) -> bool:
        return self.role == self.Role.ORGANIZER

    @property
    def is_admin_role(self) -> bool:
        return self.is_staff or self.is_superuser or self.role == self.Role.ADMIN


class OAuthLoginAttempt(models.Model):
    """Single-use server record for an OAuth state value."""

    state_digest = models.CharField(max_length=64, unique=True)
    nonce_digest = models.CharField(max_length=64)
    expires_at = models.DateTimeField(db_index=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class SocialIdentity(models.Model):
    class Provider(models.TextChoices):
        GOOGLE = "google", "Google"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_identities",
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    subject = models.CharField(max_length=255)
    email_at_link = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("provider", "subject"), name="unique_social_provider_subject"
            ),
            models.UniqueConstraint(
                fields=("provider", "user"), name="unique_social_provider_user"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.provider} identity for user {self.user_id}"

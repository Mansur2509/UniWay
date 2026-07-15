from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Institution(models.Model):
    name = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class InstitutionMembership(models.Model):
    """Deliberately separate from the global `User.Role` (student/organizer/
    admin): a user's platform-level role is unrelated to their relationship
    to one specific institution. Purely additive -- never touches User or
    any existing permission class."""

    class MemberRole(models.TextChoices):
        STUDENT_MEMBER = "student_member", "Student"
        COUNSELOR = "counselor", "Counselor / advisor"
        SCHOOL_MANAGER = "school_manager", "School manager"
        ORG_MANAGER = "org_manager", "Organization manager"

    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACTIVE = "active", "Active"
        REMOVED = "removed", "Removed"
        SUSPENDED = "suspended", "Suspended"

    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="institution_memberships"
    )
    role = models.CharField(max_length=20, choices=MemberRole.choices)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INVITED)

    # Explicit, per-student, revocable consent. A counselor/manager sees
    # only what the student has actively agreed to share -- never essays or
    # application detail by default.
    shares_application_status = models.BooleanField(default=False)
    shares_essays = models.BooleanField(default=False)

    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "user"],
                condition=Q(status__in=["invited", "active"]),
                name="unique_active_membership_per_institution",
            )
        ]
        indexes = [models.Index(fields=["institution", "status"])]

    def accept(self) -> None:
        self.status = self.Status.ACTIVE
        self.joined_at = timezone.now()
        self.save(update_fields=["status", "joined_at"])

    def __str__(self) -> str:
        return f"{self.user_id}@{self.institution_id} ({self.role}, {self.status})"


class InstitutionAuditLogEntry(models.Model):
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="audit_log_entries"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    action = models.CharField(max_length=60)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.action} in institution {self.institution_id}"

"""School / enterprise dashboard foundation (POST-V1-021 Phase 6).

Every institution-scoped read filters by the requesting user's own active
membership in that exact institution -- never by the URL slug alone -- and
every sensitive access writes an `InstitutionAuditLogEntry`.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone

from services.application_service.models import ApplicationTrackerItem
from services.essay_service.models import EssayWorkspace

from .models import Institution, InstitutionAuditLogEntry, InstitutionMembership

User = get_user_model()

MANAGER_ROLES = (InstitutionMembership.MemberRole.SCHOOL_MANAGER, InstitutionMembership.MemberRole.ORG_MANAGER)
STAFF_ROLES = MANAGER_ROLES + (InstitutionMembership.MemberRole.COUNSELOR,)


class InstitutionAccessError(Exception):
    """Raised when the requesting user has no active, sufficiently-
    privileged membership in the target institution."""


def get_active_membership(*, user, institution: Institution) -> InstitutionMembership | None:
    return InstitutionMembership.objects.filter(
        institution=institution, user=user, status=InstitutionMembership.Status.ACTIVE
    ).first()


def require_staff_membership(*, user, institution: Institution) -> InstitutionMembership:
    membership = get_active_membership(user=user, institution=institution)
    if membership is None or membership.role not in STAFF_ROLES:
        raise InstitutionAccessError("You do not have staff access to this institution.")
    return membership


def require_manager_membership(*, user, institution: Institution) -> InstitutionMembership:
    membership = get_active_membership(user=user, institution=institution)
    if membership is None or membership.role not in MANAGER_ROLES:
        raise InstitutionAccessError("You do not have manager access to this institution.")
    return membership


def log_action(*, institution: Institution, actor, action: str, target_user=None, metadata=None) -> None:
    InstitutionAuditLogEntry.objects.create(
        institution=institution,
        actor=actor,
        action=action,
        target_user=target_user,
        metadata=metadata or {},
    )


def invite_member(*, institution: Institution, inviter, email: str, role: str) -> InstitutionMembership:
    require_manager_membership(user=inviter, institution=institution)
    invited_user = User.objects.filter(email__iexact=email).first()
    if invited_user is None:
        raise ValueError("No UniWay account exists for that email yet.")

    membership, created = InstitutionMembership.objects.get_or_create(
        institution=institution,
        user=invited_user,
        defaults={"role": role, "invited_by": inviter},
    )
    if not created and membership.status == InstitutionMembership.Status.REMOVED:
        membership.status = InstitutionMembership.Status.INVITED
        membership.role = role
        membership.invited_by = inviter
        membership.joined_at = None
        membership.save(update_fields=["status", "role", "invited_by", "joined_at"])

    log_action(
        institution=institution,
        actor=inviter,
        action="invite_member",
        target_user=invited_user,
        metadata={"role": role},
    )
    return membership


def accept_invitation(*, membership: InstitutionMembership, user) -> InstitutionMembership:
    if membership.user_id != user.id:
        raise InstitutionAccessError("This invitation does not belong to your account.")
    if membership.status != InstitutionMembership.Status.INVITED:
        raise ValueError("This invitation is no longer pending.")
    membership.accept()
    return membership


def set_removed(*, institution: Institution, manager, membership: InstitutionMembership) -> None:
    require_manager_membership(user=manager, institution=institution)
    membership.status = InstitutionMembership.Status.REMOVED
    membership.removed_at = timezone.now()
    membership.save(update_fields=["status", "removed_at"])
    log_action(
        institution=institution, actor=manager, action="remove_member", target_user=membership.user
    )


def student_summary_rows(*, institution: Institution, viewer) -> list[dict]:
    """Staff-facing student list. A non-consenting student appears with
    name + membership status only -- never application/essay detail.

    Application/essay counts are fetched in two grouped queries covering
    every consenting student at once, not one query per student -- this
    view's cost must stay flat as an institution's roster grows."""
    require_staff_membership(user=viewer, institution=institution)

    student_memberships = list(
        InstitutionMembership.objects.filter(
            institution=institution,
            role=InstitutionMembership.MemberRole.STUDENT_MEMBER,
            status=InstitutionMembership.Status.ACTIVE,
        ).select_related("user")
    )

    application_sharing_ids = [
        m.user_id for m in student_memberships if m.shares_application_status
    ]
    essay_sharing_ids = [m.user_id for m in student_memberships if m.shares_essays]

    applications_by_user: dict[int, dict[str, int]] = {}
    if application_sharing_ids:
        counts = (
            ApplicationTrackerItem.objects.filter(
                user_id__in=application_sharing_ids, archived_at__isnull=True
            )
            .values("user_id", "status")
            .annotate(count=Count("id"))
        )
        for row in counts:
            applications_by_user.setdefault(row["user_id"], {})[row["status"]] = row["count"]

    essay_counts_by_user: dict[int, int] = {}
    if essay_sharing_ids:
        essay_counts_by_user = {
            row["user_id"]: row["count"]
            for row in (
                EssayWorkspace.objects.filter(user_id__in=essay_sharing_ids)
                .values("user_id")
                .annotate(count=Count("id"))
            )
        }

    rows = [
        {
            "user_id": membership.user_id,
            "full_name": getattr(membership.user, "get_full_name", lambda: "")() or membership.user.email,
            "shares_application_status": membership.shares_application_status,
            "shares_essays": membership.shares_essays,
            "applications_by_status": (
                applications_by_user.get(membership.user_id, {})
                if membership.shares_application_status
                else None
            ),
            "essay_count": (
                essay_counts_by_user.get(membership.user_id, 0) if membership.shares_essays else None
            ),
        }
        for membership in student_memberships
    ]

    log_action(institution=institution, actor=viewer, action="view_student_list")
    return rows


def institution_analytics(*, institution: Institution, viewer) -> dict:
    require_staff_membership(user=viewer, institution=institution)
    active_students = InstitutionMembership.objects.filter(
        institution=institution,
        role=InstitutionMembership.MemberRole.STUDENT_MEMBER,
        status=InstitutionMembership.Status.ACTIVE,
    )
    consenting_ids = active_students.filter(shares_application_status=True).values_list(
        "user_id", flat=True
    )
    return {
        "active_student_count": active_students.count(),
        "consenting_student_count": consenting_ids.count(),
        "applications_created_total": ApplicationTrackerItem.objects.filter(
            user_id__in=list(consenting_ids), archived_at__isnull=True
        ).count(),
    }

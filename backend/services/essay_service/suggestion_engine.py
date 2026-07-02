from dataclasses import dataclass
from datetime import date

from django.utils import timezone

from services.application_service.models import ApplicationTrackerItem
from services.university_service.deadline_normalization import (
    normalize_university_deadline,
)
from services.university_service.models import (
    SavedUniversity,
    University,
    UniversityFieldVerification,
)

from .models import EssayWorkspace


@dataclass(frozen=True)
class EssaySuggestionResult:
    created: list[EssayWorkspace]
    existing: list[EssayWorkspace]


@dataclass(frozen=True)
class EssayTarget:
    university: University
    application: ApplicationTrackerItem | None = None


def generate_essay_suggestions(user) -> EssaySuggestionResult:
    """Create idempotent, source-aware essay workspace suggestions.

    The generator creates planning drafts only. It never writes essay text,
    never claims an unverified official prompt, and never reopens skipped
    suggestions.
    """

    targets = _collect_targets(user)
    created: list[EssayWorkspace] = []
    existing: list[EssayWorkspace] = []

    if targets:
        essay, was_created = _create_if_missing(
            user=user,
            suggestion_key="common_app:global",
            defaults={
                "title": "Common App personal statement",
                "essay_type": EssayWorkspace.EssayType.COMMON_APP,
                "status": EssayWorkspace.Status.SUGGESTED,
                "priority": EssayWorkspace.Priority.HIGH,
                "prompt_text": (
                    "Use the current official application platform prompt list. "
                    "Do not draft from memory until you confirm the prompt."
                ),
                "prompt_verification_status": EssayWorkspace.VerificationStatus.NEEDS_VERIFICATION,
                "prompt_confidence": EssayWorkspace.Confidence.LOW,
                "notes": "Suggested because you have at least one shortlisted or tracked university.",
            },
        )
        (created if was_created else existing).append(essay)

    for target in targets:
        essay, was_created = _create_university_supplement(user, target)
        (created if was_created else existing).append(essay)
        scholarship = _create_scholarship_essay(user, target)
        if scholarship is not None:
            scholarship_essay, scholarship_created = scholarship
            (created if scholarship_created else existing).append(scholarship_essay)

    return EssaySuggestionResult(created=created, existing=existing)


def _collect_targets(user) -> list[EssayTarget]:
    applications = (
        ApplicationTrackerItem.objects.filter(user=user)
        .select_related("university")
        .prefetch_related(
            "university__field_verifications",
            "university__scholarships",
        )
        .order_by("deadline", "-updated_at")
    )
    saved_universities = (
        SavedUniversity.objects.filter(user=user)
        .select_related("university")
        .prefetch_related(
            "university__field_verifications",
            "university__scholarships",
        )
        .order_by("-created_at")
    )

    targets_by_university: dict[int, EssayTarget] = {}
    for application in applications:
        targets_by_university[application.university_id] = EssayTarget(
            university=application.university,
            application=application,
        )
    for saved in saved_universities:
        targets_by_university.setdefault(
            saved.university_id,
            EssayTarget(university=saved.university),
        )
    return list(targets_by_university.values())


def _create_university_supplement(user, target: EssayTarget) -> tuple[EssayWorkspace, bool]:
    university = target.university
    verification = _field_verification(university, "essay_requirements")
    has_prompt_text = bool(university.essay_requirements.strip())
    prompt_status, confidence = _prompt_status(has_prompt_text, verification)
    source_url = _source_url(university, verification)
    due_date = _due_date(target, user)
    key_prefix = (
        f"application:{target.application.id}"
        if target.application
        else f"university:{university.id}"
    )

    return _create_if_missing(
        user=user,
        suggestion_key=f"{key_prefix}:supplement",
        defaults={
            "title": f"{university.name}: verify supplemental essays",
            "essay_type": EssayWorkspace.EssayType.SUPPLEMENT,
            "university": university,
            "application": target.application,
            "status": EssayWorkspace.Status.SUGGESTED,
            "priority": _priority_for_due_date(due_date),
            "due_date": due_date,
            "prompt_text": (
                university.essay_requirements.strip()
                if has_prompt_text
                else "Prompt needs verification. Check the official application portal before drafting."
            ),
            "prompt_verification_status": prompt_status,
            "prompt_confidence": confidence,
            "source_url": source_url,
            "notes": (
                f"You have tracked {university.name}. Review verified essay requirements "
                "and keep each required essay as a separate draft."
            ),
        },
    )


def _create_scholarship_essay(user, target: EssayTarget) -> tuple[EssayWorkspace, bool] | None:
    university = target.university
    has_aid_signal = bool(
        university.scholarship_available
        or university.scholarships.all()
        or university.scholarships_text.strip()
        or university.financial_aid_url
    )
    if not has_aid_signal:
        return None

    due_date = target.application.scholarship_deadline if target.application else None
    key_prefix = (
        f"application:{target.application.id}"
        if target.application
        else f"university:{university.id}"
    )
    return _create_if_missing(
        user=user,
        suggestion_key=f"{key_prefix}:scholarship",
        defaults={
            "title": f"{university.name}: verify scholarship essay requirements",
            "essay_type": EssayWorkspace.EssayType.SCHOLARSHIP,
            "university": university,
            "application": target.application,
            "status": EssayWorkspace.Status.SUGGESTED,
            "priority": _priority_for_due_date(due_date),
            "due_date": due_date,
            "prompt_text": (
                university.scholarships_text.strip()
                or "Scholarship essay requirements need verification. Check the official financial aid or scholarship page."
            ),
            "prompt_verification_status": EssayWorkspace.VerificationStatus.NEEDS_VERIFICATION,
            "prompt_confidence": EssayWorkspace.Confidence.LOW,
            "source_url": university.financial_aid_url or university.official_website,
            "notes": "Suggested because this university has a scholarship or financial aid signal.",
        },
    )


def _create_if_missing(user, suggestion_key: str, defaults: dict) -> tuple[EssayWorkspace, bool]:
    existing = EssayWorkspace.objects.filter(
        user=user,
        suggestion_key=suggestion_key,
    ).first()
    if existing is not None:
        return existing, False

    essay = EssayWorkspace.objects.create(
        user=user,
        suggestion_key=suggestion_key,
        **defaults,
    )
    return essay, True


def _field_verification(university: University, field_name: str) -> UniversityFieldVerification | None:
    return next(
        (
            verification
            for verification in university.field_verifications.all()
            if verification.field_name == field_name
        ),
        None,
    )


def _prompt_status(
    has_prompt_text: bool,
    verification: UniversityFieldVerification | None,
) -> tuple[str, str]:
    if not has_prompt_text:
        return (
            EssayWorkspace.VerificationStatus.MISSING,
            EssayWorkspace.Confidence.LOW,
        )
    if verification is None:
        return (
            EssayWorkspace.VerificationStatus.NEEDS_VERIFICATION,
            EssayWorkspace.Confidence.MEDIUM,
        )
    if verification.status == UniversityFieldVerification.Status.VERIFIED:
        return (
            EssayWorkspace.VerificationStatus.VERIFIED,
            EssayWorkspace.Confidence.HIGH,
        )
    return (
        EssayWorkspace.VerificationStatus.NEEDS_VERIFICATION,
        EssayWorkspace.Confidence.MEDIUM,
    )


def _source_url(
    university: University,
    verification: UniversityFieldVerification | None,
) -> str:
    if verification is not None:
        return verification.source_url
    return university.application_portal_url or university.admissions_url or university.official_website


def _due_date(target: EssayTarget, user) -> date | None:
    if target.application and target.application.deadline:
        return target.application.deadline
    profile = getattr(user, "student_profile", None)
    return normalize_university_deadline(target.university, profile).display_date


def _priority_for_due_date(due_date: date | None) -> str:
    if due_date is None:
        return EssayWorkspace.Priority.MEDIUM
    days = (due_date - timezone.now().date()).days
    if days <= 14:
        return EssayWorkspace.Priority.URGENT
    if days <= 60:
        return EssayWorkspace.Priority.HIGH
    return EssayWorkspace.Priority.MEDIUM

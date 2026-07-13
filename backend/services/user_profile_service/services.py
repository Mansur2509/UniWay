from dataclasses import dataclass

from django.db import transaction

from .models import (
    StudentProfile,
    UserPreference,
)


@dataclass(frozen=True)
class ProfileCompletion:
    percentage: int
    completed_fields: int
    total_fields: int
    missing_fields: list[str]
    missing_sections: list[str]
    required_fields: list[str]
    is_complete: bool
    can_complete: bool


REQUIRED_ONBOARDING_SECTIONS = (
    "identity",
    "academic",
    "exams",
    "activities",
    "support",
)


@transaction.atomic
def ensure_profile_records(user) -> tuple[StudentProfile, UserPreference]:
    profile, _ = StudentProfile.objects.select_for_update().get_or_create(user=user)
    preferences, _ = UserPreference.objects.select_for_update().get_or_create(user=user)
    return profile, preferences


def get_profile_records_for_read(user) -> tuple[StudentProfile, UserPreference]:
    """Return persisted records or unsaved defaults without writing on GET."""

    profile = StudentProfile.objects.filter(user=user).first()
    preferences = UserPreference.objects.filter(user=user).first()
    return (
        profile if profile is not None else StudentProfile(user=user),
        preferences if preferences is not None else UserPreference(user=user),
    )


def calculate_profile_completion(
    profile: StudentProfile,
    preferences: UserPreference,
) -> ProfileCompletion:
    checks = {
        "full_name": bool(profile.full_name.strip()),
        "birth_date": profile.birth_date is not None,
        "country": bool(profile.country.strip()),
        "city": bool(profile.city.strip()),
        "school_or_university": bool(profile.school_or_university.strip()),
        "grade": bool(profile.grade.strip()),
        "education_status": bool(profile.education_status.strip()),
        "expected_graduation_year": profile.expected_graduation_year is not None,
        "gpa": profile.gpa is not None and profile.gpa_scale is not None,
        "intended_degree": bool(profile.intended_degree.strip()),
        "target_countries": bool(profile.target_countries),
        "target_universities": bool(profile.target_universities) or profile.university_unsure,
        "intended_majors": bool(profile.intended_majors) or profile.major_unsure,
        "scholarship_need": bool(profile.scholarship_need),
        "interested_classes": bool(preferences.interested_classes),
        "preparation_needs": bool(profile.preparation_needs),
        "essay_status": bool(profile.essay_status),
        "support_priorities": bool(profile.support_priorities),
    }

    completed_sections = set(profile.onboarding_sections)
    section_checks = {
        section: section in completed_sections for section in REQUIRED_ONBOARDING_SECTIONS
    }
    all_checks = {**checks, **{f"section:{key}": value for key, value in section_checks.items()}}
    completed_fields = sum(all_checks.values())
    total_fields = len(all_checks)
    percentage = round((completed_fields / total_fields) * 100)
    missing_fields = [field for field, completed in checks.items() if not completed]
    missing_sections = [
        section for section, completed in section_checks.items() if not completed
    ]
    can_complete = not missing_fields and not missing_sections
    return ProfileCompletion(
        percentage=percentage,
        completed_fields=completed_fields,
        total_fields=total_fields,
        missing_fields=missing_fields,
        missing_sections=missing_sections,
        required_fields=list(checks),
        is_complete=bool(profile.onboarding_completed_at and can_complete),
        can_complete=can_complete,
    )

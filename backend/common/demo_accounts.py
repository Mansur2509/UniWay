"""Shared definition of the public student demo account.

Both `seed_demo --with-demo-data` (full local/dev dataset seeding, never run
on production web-service startup) and the lightweight `ensure_demo_accounts`
command (safe to run against production) need to create or repair the same
account, so its email, password, and profile content live here once instead
of being duplicated across files.
"""

from __future__ import annotations

from datetime import date

from django.utils import timezone

from services.user_profile_service.services import ensure_profile_records

CANONICAL_STUDENT_DEMO_EMAIL = "student.demo@uniway.local"

# Known prior emails for this same public demo account, oldest first. Used
# only to migrate the account in place (preserving its id and any demo
# history already attached to it) rather than creating a second, orphaned
# account when the canonical email doesn't exist yet.
LEGACY_STUDENT_DEMO_EMAILS: tuple[str, ...] = ("student.demo@eduverse.local",)

DEMO_PASSWORD = "UniWay-Demo-842!"  # nosec B105 - public student sample account only


def populate_demo_student_profile(user) -> None:
    """Fill in a complete, safe, non-personal demo profile for the public
    student account. Contains no real personal information."""
    profile, preferences = ensure_profile_records(user)
    profile.full_name = "UniWay Demo Student"
    profile.birth_date = date(2004, 4, 12)
    profile.country = "Uzbekistan"
    profile.city = "Tashkent"
    profile.school_or_university = "UniWay Demo Academy"
    profile.grade = "12"
    profile.expected_graduation_year = timezone.now().year + 1
    profile.education_status = "school_student"
    profile.gpa = "4.50"
    profile.gpa_scale = "5.00"
    profile.intended_degree = "bachelor"
    profile.intended_major = "Computer Science"
    profile.intended_majors = ["Computer Science", "Economics"]
    profile.target_countries = ["United States", "United Kingdom"]
    profile.target_universities = []
    profile.university_unsure = True
    profile.major_unsure = False
    profile.test_scores = {"sat": 1450, "ielts": 7.5}
    profile.exam_plans = {
        "taken": [],
        "planned": [
            {
                "name": "SAT",
                "date": f"{timezone.now().year + 1}-03-13",
                "target_score": "1500",
            }
        ],
    }
    profile.preparation_needs = ["SAT preparation"]
    profile.activities = {
        "extracurriculars": ["Coding club"],
        "honors": [],
        "sports": [],
        "olympiads": [],
        "research_projects": ["Demo research project"],
        "mun_debate": [],
        "volunteering": ["Peer tutoring"],
        "leadership": [],
        "work_internships": [],
    }
    profile.essay_status = "not_yet"
    profile.essay_stage = "planning"
    profile.support_priorities = ["University research"]
    profile.scholarship_need = "yes"
    profile.onboarding_sections = ["identity", "academic", "exams", "activities", "support"]
    profile.onboarding_completed_at = timezone.now()
    profile.telegram_username = "@uniway_demo_student"
    profile.save()

    preferences.interested_classes = ["SAT Math", "AP Computer Science", "Research Basics"]
    preferences.career_interests = ["Technology", "Research"]
    preferences.interests = ["Events", "Academic planning"]
    preferences.research_interest = True
    preferences.save()


def _harden_as_public_student_demo(user) -> None:
    """Guarantee the account can never be privileged and its password
    matches the documented demo credential, regardless of how it got here."""
    user.role = user.Role.STUDENT
    user.is_staff = False
    user.is_superuser = False
    user.is_active = True
    user.set_password(DEMO_PASSWORD)
    user.save(update_fields=["role", "is_staff", "is_superuser", "is_active", "password"])
    populate_demo_student_profile(user)


def ensure_canonical_student_demo_account(user_model) -> dict[str, str | bool]:
    """Idempotently ensure exactly one active public student demo account
    exists at `CANONICAL_STUDENT_DEMO_EMAIL`.

    If a legacy-email account exists and the canonical one doesn't, the
    legacy account is renamed in place (its id, and anything already linked
    to it, is preserved) rather than creating a second, orphaned account.
    Any other still-active legacy-email account found afterwards is
    deactivated so at most one demo account is ever reachable. Never
    touches an account that isn't one of the known demo emails, and never
    grants staff/superuser/organizer/admin access.

    Returns a status report (no credentials).
    """
    canonical = user_model.objects.filter(email__iexact=CANONICAL_STUDENT_DEMO_EMAIL).first()
    action = "unchanged"

    if canonical is None:
        legacy = None
        for legacy_email in LEGACY_STUDENT_DEMO_EMAILS:
            legacy = user_model.objects.filter(email__iexact=legacy_email).first()
            if legacy is not None:
                break

        if legacy is not None:
            legacy.email = CANONICAL_STUDENT_DEMO_EMAIL
            legacy.username = CANONICAL_STUDENT_DEMO_EMAIL
            legacy.save(update_fields=["email", "username"])
            canonical = legacy
            action = "migrated_legacy_account"
        else:
            canonical = user_model.objects.create_user(
                username=CANONICAL_STUDENT_DEMO_EMAIL,
                email=CANONICAL_STUDENT_DEMO_EMAIL,
                password=DEMO_PASSWORD,
                role=user_model.Role.STUDENT,
            )
            action = "created_new_account"
    else:
        action = "already_present"

    _harden_as_public_student_demo(canonical)

    deactivated_duplicates = []
    for legacy_email in LEGACY_STUDENT_DEMO_EMAILS:
        duplicate = (
            user_model.objects.filter(email__iexact=legacy_email)
            .exclude(pk=canonical.pk)
            .first()
        )
        if duplicate is not None and duplicate.is_active:
            duplicate.is_active = False
            duplicate.save(update_fields=["is_active"])
            deactivated_duplicates.append(duplicate.email)

    return {
        "email": canonical.email,
        "action": action,
        "deactivated_duplicates": deactivated_duplicates,
    }

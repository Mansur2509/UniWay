"""Default requirement-checklist generation for an application tracker item.

Every generated row is grounded in real data already on the university
record (or a small set of near-universal checklist items every application
needs regardless of school). Free-text university fields are copied as-is
into the description -- never split or reinterpreted into invented
sub-requirements. Generation is one-time and idempotent: if the application
already has any requirements, calling this again is a no-op.
"""

from __future__ import annotations

from .models import ApplicationRequirement

_BASELINE_ITEMS = (
    (
        ApplicationRequirement.RequirementType.APPLICATION_FEE,
        "Application fee",
        "Check the university's official application portal for the exact fee amount and payment method.",
    ),
    (
        ApplicationRequirement.RequirementType.TRANSCRIPT,
        "Official transcript",
        "Most universities require an official academic transcript submitted directly by your school.",
    ),
)


def generate_default_requirements(application) -> list[ApplicationRequirement]:
    """Seed a starter checklist for ``application`` from university data.

    Returns the existing requirements unchanged if any already exist for
    this application, so calling this endpoint twice never duplicates rows.
    """
    existing = list(application.requirements.all())
    if existing:
        return existing

    university = application.university
    rows: list[ApplicationRequirement] = []
    order = 0

    for requirement_type, title, description in _BASELINE_ITEMS:
        rows.append(
            ApplicationRequirement(
                application=application,
                requirement_type=requirement_type,
                title=title,
                description=description,
                source=ApplicationRequirement.Source.SYSTEM_GENERATED,
                order=order,
            )
        )
        order += 1

    if university.essay_requirements.strip():
        rows.append(
            ApplicationRequirement(
                application=application,
                requirement_type=ApplicationRequirement.RequirementType.ESSAY,
                title="Essays",
                description=university.essay_requirements,
                source=ApplicationRequirement.Source.UNIVERSITY_DATA,
                order=order,
            )
        )
        order += 1

    if university.ap_recommendations.strip():
        rows.append(
            ApplicationRequirement(
                application=application,
                requirement_type=ApplicationRequirement.RequirementType.RECOMMENDATION,
                title="Recommendation letters",
                description=university.ap_recommendations,
                source=ApplicationRequirement.Source.UNIVERSITY_DATA,
                order=order,
            )
        )
        order += 1

    if university.test_policy:
        description = (
            university.standardized_testing_policy_text.strip()
            or f"This university's standardized testing policy is: {university.get_test_policy_display()}."
        )
        rows.append(
            ApplicationRequirement(
                application=application,
                requirement_type=ApplicationRequirement.RequirementType.TEST_SCORES,
                title="Standardized test scores",
                description=description,
                is_required=university.test_policy == university.TestPolicy.REQUIRED,
                source=ApplicationRequirement.Source.UNIVERSITY_DATA,
                order=order,
            )
        )
        order += 1

    for university_requirement in university.requirements.all():
        rows.append(
            ApplicationRequirement(
                application=application,
                requirement_type=ApplicationRequirement.RequirementType.OTHER,
                title=university_requirement.value,
                description=university_requirement.notes,
                source=ApplicationRequirement.Source.UNIVERSITY_DATA,
                order=order,
            )
        )
        order += 1

    return ApplicationRequirement.objects.bulk_create(rows)

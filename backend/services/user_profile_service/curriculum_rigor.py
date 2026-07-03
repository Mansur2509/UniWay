from __future__ import annotations

from dataclasses import dataclass

CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"

# Curricula that structurally include advanced coursework by design. This is a
# context signal only — it never implies one diploma is "worth more" than
# another, only that advanced-course context is more likely to be present.
RIGOR_HIGH_CURRICULA = {"ib", "a_level", "ap", "academic_lyceum"}

STEM_KEYWORDS = (
    "engineering", "computer", "computing", "science", "math", "physics",
    "biology", "chemistry", "data", "technology", "statistics",
)
HUMANITIES_KEYWORDS = (
    "history", "literature", "philosophy", "language", "art", "linguistics",
    "sociology", "anthropology", "political", "psychology",
)
BUSINESS_ECONOMICS_KEYWORDS = (
    "business", "economics", "finance", "management", "accounting", "marketing",
)

RECOMMENDED_COURSEWORK_BY_CLUSTER = {
    "stem": ("ap_calculus", "ap_computer_science", "ap_physics", "ap_chemistry", "ap_biology"),
    "humanities": ("ap_english_literature", "ap_history", "ap_psychology", "ap_language"),
    "business": ("ap_economics", "ap_statistics", "ap_computer_science"),
}


@dataclass(frozen=True)
class CurriculumRigorResult:
    curriculum_context: str
    rigor_score: int
    rigor_confidence: str
    missing_curriculum_data: list[str]
    stem_rigor_signal: str
    humanities_rigor_signal: str
    business_economics_rigor_signal: str


def _advanced_course_total(profile) -> int:
    counts = (
        profile.ap_courses_count,
        profile.ib_courses_count,
        profile.a_level_subjects_count,
    )
    return sum(count for count in counts if count is not None)


def _has_course_count_data(profile) -> bool:
    return any(
        value is not None
        for value in (
            profile.ap_courses_count,
            profile.ib_courses_count,
            profile.a_level_subjects_count,
            profile.honors_courses_count,
        )
    )


def _profile_majors(profile) -> list[str]:
    return [
        str(value).strip().lower()
        for value in (profile.intended_majors or ([profile.intended_major] if profile.intended_major else []))
        if str(value).strip()
    ]


def _domain_signal(majors: list[str], keywords: tuple[str, ...], advanced_total: int) -> str:
    if not majors or not any(keyword in major for major in majors for keyword in keywords):
        return "unknown"
    if advanced_total >= 3:
        return "high"
    if advanced_total >= 1:
        return "medium"
    return "low"


def calculate_curriculum_rigor(profile) -> CurriculumRigorResult:
    """Context-signal only estimate of curriculum rigor. Never a claim that one
    diploma is officially "worth more" than another — unknown data always
    lowers confidence rather than being guessed at.
    """

    missing: list[str] = []
    curriculum_type = profile.curriculum_type

    if curriculum_type == profile.CurriculumType.UNKNOWN:
        missing.append("curriculum_type")

    has_course_counts = _has_course_count_data(profile)
    if not has_course_counts:
        missing.append("advanced_course_counts")

    advanced_total = _advanced_course_total(profile)
    honors_total = profile.honors_courses_count or 0

    rigor_score = 45
    if curriculum_type in RIGOR_HIGH_CURRICULA:
        rigor_score += 15
    if advanced_total >= 6:
        rigor_score += 20
    elif advanced_total >= 3:
        rigor_score += 12
    elif advanced_total >= 1:
        rigor_score += 6
    if honors_total >= 3:
        rigor_score += 8
    if profile.course_rigor_level == profile.CourseRigorLevel.HIGHLY_ADVANCED:
        rigor_score += 10
    elif profile.course_rigor_level == profile.CourseRigorLevel.ADVANCED:
        rigor_score += 5
    rigor_score = max(1, min(100, rigor_score))

    if curriculum_type == profile.CurriculumType.UNKNOWN and not has_course_counts:
        confidence = CONFIDENCE_LOW
    elif has_course_counts and curriculum_type != profile.CurriculumType.UNKNOWN:
        confidence = CONFIDENCE_HIGH
    else:
        confidence = CONFIDENCE_MEDIUM

    curriculum_context = (
        profile.get_curriculum_type_display()
        if curriculum_type != profile.CurriculumType.UNKNOWN
        else "unknown"
    )

    majors = _profile_majors(profile)
    return CurriculumRigorResult(
        curriculum_context=curriculum_context,
        rigor_score=rigor_score,
        rigor_confidence=confidence,
        missing_curriculum_data=missing,
        stem_rigor_signal=_domain_signal(majors, STEM_KEYWORDS, advanced_total),
        humanities_rigor_signal=_domain_signal(majors, HUMANITIES_KEYWORDS, advanced_total),
        business_economics_rigor_signal=_domain_signal(majors, BUSINESS_ECONOMICS_KEYWORDS, advanced_total),
    )


def calculate_major_curriculum_fit(profile, program_or_major: str | None) -> dict:
    """Context-only "preparation signal" for a specific program/major, derived
    from advanced-course counts. Never an official equivalency claim.
    """

    program = (program_or_major or "").strip().lower()
    if not program:
        return {
            "preparation_signal": "unknown",
            "recommended_coursework": [],
            "note": "No target program provided; preparation signal unavailable.",
        }

    advanced_total = _advanced_course_total(profile)
    cluster = None
    if any(keyword in program for keyword in STEM_KEYWORDS):
        cluster = "stem"
    elif any(keyword in program for keyword in BUSINESS_ECONOMICS_KEYWORDS):
        cluster = "business"
    elif any(keyword in program for keyword in HUMANITIES_KEYWORDS):
        cluster = "humanities"

    if cluster is None:
        return {
            "preparation_signal": "unknown",
            "recommended_coursework": [],
            "note": "Program category not recognized for curriculum-fit context.",
        }

    if advanced_total >= 3:
        signal = "strong_context"
    elif advanced_total >= 1:
        signal = "some_context"
    else:
        signal = "limited_context"

    return {
        "preparation_signal": signal,
        "recommended_coursework": list(RECOMMENDED_COURSEWORK_BY_CLUSTER.get(cluster, ())),
        "note": "Preparation signal is a context estimate from advanced coursework, not an official equivalency.",
    }

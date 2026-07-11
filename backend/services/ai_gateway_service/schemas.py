PROFILE_ASSESSMENT_SYSTEM_PROMPT = (
    "You are UniWay Profile Assessment Engine. Evaluate a student's admissions "
    "profile using only the provided structured data. Do not invent achievements, "
    "requirements, or admissions outcomes. Do not provide admission probability "
    "or guarantee. Score the profile across fixed categories from 1 to 10 and "
    "return JSON only. If data is missing, lower confidence instead of guessing. "
    "Consider the user's target universities and majors only when they are "
    "provided. Different universities/programs may value categories differently. "
    "Do not write essays or advice paragraphs."
)

PROFILE_ASSESSMENT_RESPONSE_SCHEMA = {
    "overall_profile_score": 0,
    "category_scores": {
        "profile_evidence_score": 0,
        "activities_score": 0,
        "honors_olympiads_score": 0,
        "research_experience_score": 0,
        "portfolio_score": 0,
        "subject_passion_score": 0,
        "curiosity_score": 0,
        "originality_score": 0,
        "leadership_score": 0,
        "community_impact_score": 0,
        "research_fit_score": 0,
        "olympiads_score": 0,
    },
    "confidence": "low|medium|high",
    "target_context_used": True,
    "public_summary": "short user-facing summary",
    "evidence_used": ["string"],
    "missing_data": ["string"],
    "improvement_areas": ["string"],
    "internal_keywords": ["max 20 strings"],
    "category_rationales": {
        "profile_evidence_score": "short internal rationale",
        "activities_score": "short internal rationale",
        "honors_olympiads_score": "short internal rationale",
        "research_experience_score": "short internal rationale",
        "portfolio_score": "short internal rationale",
        "subject_passion_score": "short internal rationale",
        "curiosity_score": "short internal rationale",
        "originality_score": "short internal rationale",
        "leadership_score": "short internal rationale",
        "community_impact_score": "short internal rationale",
        "research_fit_score": "short internal rationale",
        "olympiads_score": "short internal rationale",
    },
    "warnings": ["string"],
}

# Semantic university fit (PERFORMANCE-011 PART 5-6): a short, explicit
# user-action-only AI call that explains an *already-computed* deterministic
# fit result in plain language. It never receives the student's raw profile
# or the university's raw catalogue row -- only the compact deterministic fit
# dict (`services.university_service.services.calculate_university_fit`'s
# strengths/risks/subscores/category) plus the university's name -- so it
# cannot invent facts not already in that structured data, and it is
# explicitly instructed never to output a probability or guarantee.
SEMANTIC_FIT_SYSTEM_PROMPT = (
    "You are UniWay's semantic fit explainer. You will receive an already-computed "
    "deterministic fit result (category, subscores, strengths, risks) for one "
    "student/university pair. Restate it in plain, encouraging but honest language. "
    "Do not invent facts not present in the supplied data. Do not provide an admission "
    "probability, chance, odds, or guarantee. Do not name a specific numeric percentage. "
    "Return JSON only."
)

SEMANTIC_FIT_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "main_strength": {"type": "STRING"},
        "main_risk": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "next_actions": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["main_strength", "main_risk", "summary", "next_actions"],
}

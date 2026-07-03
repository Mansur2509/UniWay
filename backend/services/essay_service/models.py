from django.conf import settings
from django.db import models
from django.db.models import Q

from common.validators import validate_http_url


class EssayWorkspace(models.Model):
    class EssayType(models.TextChoices):
        COMMON_APP = "common_app", "Common App personal statement"
        SUPPLEMENT = "supplement", "Supplement"
        SCHOLARSHIP = "scholarship", "Scholarship"
        ACTIVITY = "activity", "Activity description"
        INTELLECTUAL_INTEREST = "intellectual_interest", "Intellectual interest"
        WHY_MAJOR = "why_major", "Why this major"
        WHY_SCHOOL = "why_school", "Why this school"
        ADDITIONAL_INFORMATION = "additional_information", "Additional information"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SUGGESTED = "suggested", "Suggested"
        PLANNED = "planned", "Planned"
        NOT_STARTED = "not_started", "Not started"
        DRAFTING = "drafting", "Drafting"
        NEEDS_REVISION = "needs_revision", "Needs revision"
        REVIEWED = "reviewed", "Reviewed"
        READY = "ready", "Ready"
        SUBMITTED = "submitted", "Submitted"
        SKIPPED = "skipped", "Skipped"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class VerificationStatus(models.TextChoices):
        VERIFIED = "verified", "Verified"
        NEEDS_VERIFICATION = "needs_verification", "Needs verification"
        MISSING = "missing", "Missing"

    class Confidence(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="essay_workspaces"
    )
    university = models.ForeignKey(
        "university_service.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="essay_workspaces",
    )
    application = models.ForeignKey(
        "application_service.ApplicationTrackerItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="essay_workspaces",
    )
    title = models.CharField(max_length=240)
    essay_type = models.CharField(max_length=30, choices=EssayType.choices, default=EssayType.OTHER)
    prompt_text = models.TextField(blank=True)
    word_limit = models.PositiveSmallIntegerField(null=True, blank=True)
    draft_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    due_date = models.DateField(null=True, blank=True)
    prompt_verification_status = models.CharField(
        max_length=24,
        choices=VerificationStatus.choices,
        default=VerificationStatus.MISSING,
    )
    prompt_confidence = models.CharField(
        max_length=12, choices=Confidence.choices, default=Confidence.LOW
    )
    source_url = models.URLField(blank=True, validators=[validate_http_url])
    notes = models.TextField(max_length=2000, blank=True)
    suggestion_key = models.CharField(max_length=255, blank=True, db_index=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(fields=("user", "status")),
            models.Index(fields=("user", "priority")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("user", "suggestion_key"),
                condition=~Q(suggestion_key=""),
                name="unique_essay_suggestion_per_user",
            )
        ]

    def __str__(self) -> str:
        return self.title


class EssayFeedback(models.Model):
    class OverallLabel(models.TextChoices):
        WEAK = "weak", "Weak"
        DEVELOPING = "developing", "Developing"
        SOLID = "solid", "Solid"
        STRONG = "strong", "Strong"
        EXCELLENT = "excellent", "Excellent"

    class WordLimitStatus(models.TextChoices):
        TOO_SHORT = "too_short", "Too short"
        WITHIN_LIMIT = "within_limit", "Within limit"
        TOO_LONG = "too_long", "Too long"

    essay = models.ForeignKey(
        EssayWorkspace, on_delete=models.CASCADE, related_name="feedback_entries"
    )
    overall_label = models.CharField(max_length=20, choices=OverallLabel.choices)
    structure_score = models.PositiveSmallIntegerField(null=True, blank=True)
    clarity_score = models.PositiveSmallIntegerField(null=True, blank=True)
    authenticity_score = models.PositiveSmallIntegerField(null=True, blank=True)
    specificity_score = models.PositiveSmallIntegerField(null=True, blank=True)
    grammar_score = models.PositiveSmallIntegerField(null=True, blank=True)
    prompt_fit_score = models.PositiveSmallIntegerField(null=True, blank=True)
    word_count = models.PositiveIntegerField(default=0)
    word_limit_status = models.CharField(max_length=20, choices=WordLimitStatus.choices)
    summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    issues = models.JSONField(default=list, blank=True)
    revision_tasks = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Feedback for {self.essay_id} ({self.overall_label})"


class EssayRevisionTask(models.Model):
    class Category(models.TextChoices):
        STRUCTURE = "structure", "Structure"
        CLARITY = "clarity", "Clarity"
        SPECIFICITY = "specificity", "Specificity"
        AUTHENTICITY = "authenticity", "Authenticity"
        GRAMMAR = "grammar", "Grammar"
        WORD_COUNT = "word_count", "Word count"
        PROMPT_FIT = "prompt_fit", "Prompt fit"

    class Status(models.TextChoices):
        TODO = "todo", "To do"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    essay = models.ForeignKey(
        EssayWorkspace, on_delete=models.CASCADE, related_name="revision_tasks"
    )
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("status", "-created_at")
        indexes = [models.Index(fields=("essay", "category"))]

    def __str__(self) -> str:
        return self.title


class AIEssayScoreReport(models.Model):
    """Persisted result of one AI essay-scoring call or cache hit lookup."""

    class Confidence(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class WordLimitStatus(models.TextChoices):
        UNDER = "under", "Under"
        WITHIN = "within", "Within"
        NEAR_LIMIT = "near_limit", "Near limit"
        OVER = "over", "Over"
        UNKNOWN = "unknown", "Unknown"

    class StyleSignal(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        INCONCLUSIVE = "inconclusive", "Inconclusive"

    class ClaimsSignal(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        INCONCLUSIVE = "inconclusive", "Inconclusive"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_essay_score_reports"
    )
    essay = models.ForeignKey(
        EssayWorkspace, on_delete=models.CASCADE, related_name="ai_score_reports"
    )
    application = models.ForeignKey(
        "application_service.ApplicationTrackerItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_essay_score_reports",
    )
    university = models.ForeignKey(
        "university_service.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_essay_score_reports",
    )
    program = models.ForeignKey(
        "university_service.UniversityProgram",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_essay_score_reports",
    )
    essay_text_hash = models.CharField(max_length=64, db_index=True)
    context_hash = models.CharField(max_length=64, db_index=True)
    rubric_version = models.CharField(max_length=50, default="essay_numeric_v1")
    model_provider = models.CharField(max_length=50, default="gemini")
    model_name = models.CharField(max_length=100)
    raw_output_json = models.JSONField(default=dict)
    overall_essay_readiness = models.PositiveSmallIntegerField()
    prompt_fit = models.PositiveSmallIntegerField()
    structure = models.PositiveSmallIntegerField()
    specificity_evidence = models.PositiveSmallIntegerField()
    authenticity = models.PositiveSmallIntegerField()
    language_clarity = models.PositiveSmallIntegerField()
    word_limit_discipline = models.PositiveSmallIntegerField(null=True, blank=True)
    school_program_alignment = models.PositiveSmallIntegerField(null=True, blank=True)
    confidence = models.CharField(max_length=10, choices=Confidence.choices)
    verified_context_used = models.BooleanField(default=False)
    word_count = models.PositiveIntegerField()
    word_limit_status = models.CharField(max_length=20, choices=WordLimitStatus.choices)
    ai_paraphrase_style_signal = models.CharField(max_length=20, choices=StyleSignal.choices)
    generic_language_signal = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
    )
    unsupported_claims_signal = models.CharField(max_length=20, choices=ClaimsSignal.choices)
    strength_flags = models.JSONField(default=list, blank=True)
    risk_flags = models.JSONField(default=list, blank=True)
    approximate_suggestions = models.JSONField(default=list, blank=True)
    source_warnings = models.JSONField(default=list, blank=True)
    disclaimers = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("essay", "essay_text_hash", "context_hash")),
            models.Index(fields=("user", "created_at")),
        ]

    def __str__(self) -> str:
        return f"AI score for essay {self.essay_id} ({self.overall_essay_readiness})"

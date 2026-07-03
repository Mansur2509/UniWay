from django.conf import settings
from django.db import models
from django.utils import timezone


class AIProfileAssessment(models.Model):
    class Confidence(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_assessments",
    )
    profile_snapshot_hash = models.CharField(max_length=64, db_index=True)
    assessment_version = models.CharField(max_length=40, default="2026-07-profile-v1")
    model_provider = models.CharField(max_length=40, blank=True)
    model_name = models.CharField(max_length=120, blank=True)
    raw_input_summary_json = models.JSONField(default=dict, blank=True)
    raw_output_json = models.JSONField(default=dict, blank=True)
    overall_profile_score = models.PositiveSmallIntegerField()
    profile_evidence_score = models.PositiveSmallIntegerField()
    activities_score = models.PositiveSmallIntegerField()
    honors_olympiads_score = models.PositiveSmallIntegerField()
    research_experience_score = models.PositiveSmallIntegerField()
    portfolio_score = models.PositiveSmallIntegerField()
    subject_passion_score = models.PositiveSmallIntegerField()
    curiosity_score = models.PositiveSmallIntegerField()
    originality_score = models.PositiveSmallIntegerField()
    leadership_score = models.PositiveSmallIntegerField()
    community_impact_score = models.PositiveSmallIntegerField()
    research_fit_score = models.PositiveSmallIntegerField()
    olympiads_score = models.PositiveSmallIntegerField()
    confidence = models.CharField(
        max_length=12,
        choices=Confidence.choices,
        default=Confidence.LOW,
        db_index=True,
    )
    public_summary = models.TextField(blank=True)
    evidence_used = models.JSONField(default=list, blank=True)
    missing_data = models.JSONField(default=list, blank=True)
    improvement_areas = models.JSONField(default=list, blank=True)
    internal_keywords = models.JSONField(default=list, blank=True)
    category_rationales = models.JSONField(default=dict, blank=True)
    target_context_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    is_stale = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "-created_at")),
            models.Index(fields=("user", "profile_snapshot_hash", "is_stale")),
        ]

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

    def __str__(self) -> str:
        return f"AIProfileAssessment<{self.user_id}:{self.created_at:%Y-%m-%d}>"

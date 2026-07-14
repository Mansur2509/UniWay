from django.conf import settings
from django.db import models
from django.db.models import Q

from common.validators import validate_http_url


class ApplicationTrackerItem(models.Model):
    class ApplicationRound(models.TextChoices):
        EARLY_DECISION = "early_decision", "Early decision"
        EARLY_ACTION = "early_action", "Early action"
        RESTRICTIVE_EARLY_ACTION = "restrictive_early_action", "Restrictive early action"
        SINGLE_CHOICE_EARLY_ACTION = (
            "single_choice_early_action",
            "Single-choice early action",
        )
        REGULAR_DECISION = "regular_decision", "Regular decision"
        ROLLING = "rolling", "Rolling"
        SCHOLARSHIP = "scholarship", "Scholarship"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        RESEARCHING = "researching", "Researching"
        SHORTLISTED = "shortlisted", "Shortlisted"
        PREPARING = "preparing", "Preparing"
        APPLYING = "applying", "Applying"
        SUBMITTED = "submitted", "Submitted"
        AWAITING_DECISION = "awaiting_decision", "Awaiting decision"
        ACCEPTED = "accepted", "Accepted"
        WAITLISTED = "waitlisted", "Waitlisted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        DREAM = "dream", "Dream"

    class FitTier(models.TextChoices):
        REACH = "reach", "Reach"
        COMPETITIVE = "competitive", "Competitive"
        TARGET = "target", "Target"
        SAFETY = "safety", "Safer"
        UNKNOWN = "unknown", "Not yet estimated"

    class Source(models.TextChoices):
        USER_ADDED = "user_added", "Added by student"
        ROADMAP = "roadmap", "Roadmap"
        RECOMMENDATION = "recommendation", "Recommendation"
        IMPORTED = "imported", "Imported"

    class TaskStatus(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        DRAFTING = "drafting", "Drafting"
        NEEDS_REVISION = "needs_revision", "Needs revision"
        READY = "ready", "Ready"
        SUBMITTED = "submitted", "Submitted"

    class RecommendationsStatus(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        REQUESTED = "requested", "Requested"
        RECEIVED = "received", "Received"
        SUBMITTED = "submitted", "Submitted"

    class TestScoresStatus(models.TextChoices):
        NOT_REQUIRED = "not_required", "Not required"
        PLANNED = "planned", "Planned"
        READY = "ready", "Ready"
        SENT = "sent", "Sent"

    class DocumentsStatus(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        COLLECTING = "collecting", "Collecting"
        READY = "ready", "Ready"
        SUBMITTED = "submitted", "Submitted"

    class FinancialAidStatus(models.TextChoices):
        NOT_APPLYING = "not_applying", "Not applying"
        RESEARCHING = "researching", "Researching"
        PREPARING = "preparing", "Preparing"
        SUBMITTED = "submitted", "Submitted"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="application_items"
    )
    university = models.ForeignKey(
        "university_service.University", on_delete=models.CASCADE, related_name="application_items"
    )
    target_program = models.ForeignKey(
        "university_service.UniversityProgram",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_items",
    )
    application_round = models.CharField(
        max_length=30, choices=ApplicationRound.choices, default=ApplicationRound.REGULAR_DECISION
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RESEARCHING, db_index=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    fit_tier = models.CharField(max_length=15, choices=FitTier.choices, default=FitTier.UNKNOWN)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.USER_ADDED)
    deadline = models.DateField(null=True, blank=True)
    personal_estimated_deadline = models.DateField(null=True, blank=True)
    target_intake_year = models.PositiveSmallIntegerField(null=True, blank=True)
    financial_aid_deadline = models.DateField(null=True, blank=True)
    scholarship_deadline = models.DateField(null=True, blank=True)
    essays_status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED
    )
    recommendations_status = models.CharField(
        max_length=20, choices=RecommendationsStatus.choices, default=RecommendationsStatus.NOT_STARTED
    )
    test_scores_status = models.CharField(
        max_length=20, choices=TestScoresStatus.choices, default=TestScoresStatus.NOT_REQUIRED
    )
    documents_status = models.CharField(
        max_length=20, choices=DocumentsStatus.choices, default=DocumentsStatus.NOT_STARTED
    )
    financial_aid_status = models.CharField(
        max_length=20, choices=FinancialAidStatus.choices, default=FinancialAidStatus.NOT_APPLYING
    )
    notes = models.TextField(max_length=3000, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("deadline", "-priority", "-created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "university"),
                condition=Q(archived_at__isnull=True),
                name="unique_active_application_per_university",
            )
        ]
        indexes = [
            models.Index(fields=("user", "status")),
            models.Index(
                fields=("user", "archived_at"), name="app_service_user_id_2e4444_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.university_id} application for {self.user_id}"


class ApplicationMilestone(models.Model):
    class Category(models.TextChoices):
        ESSAYS = "essays", "Essays"
        RECOMMENDATIONS = "recommendations", "Recommendations"
        TESTS = "tests", "Tests"
        FINANCIAL_AID = "financial_aid", "Financial aid"
        DOCUMENTS = "documents", "Documents"
        SUBMISSION = "submission", "Submission"
        INTERVIEW = "interview", "Interview"
        DECISION = "decision", "Decision"

    class Status(models.TextChoices):
        TODO = "todo", "To do"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    application = models.ForeignKey(
        ApplicationTrackerItem, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=240)
    category = models.CharField(max_length=20, choices=Category.choices)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    notes = models.TextField(max_length=1000, blank=True)
    linked_roadmap_task = models.ForeignKey(
        "roadmap_service.RoadmapTask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_milestones",
    )
    source_url = models.URLField(blank=True, validators=[validate_http_url])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_date", "-created_at")
        indexes = [models.Index(fields=("application", "status"))]

    def __str__(self) -> str:
        return self.title


class ApplicationRequirement(models.Model):
    class RequirementType(models.TextChoices):
        TRANSCRIPT = "transcript", "Transcript"
        TEST_SCORES = "test_scores", "Test scores"
        ENGLISH_PROOF = "english_proof", "English proficiency proof"
        ESSAY = "essay", "Essay"
        SUPPLEMENT = "supplement", "Supplement"
        RECOMMENDATION = "recommendation", "Recommendation"
        PORTFOLIO = "portfolio", "Portfolio"
        FINANCIAL_AID = "financial_aid", "Financial aid"
        PASSPORT = "passport", "Passport"
        APPLICATION_FEE = "application_fee", "Application fee"
        INTERVIEW = "interview", "Interview"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        MISSING = "missing", "Missing"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        WAIVED = "waived", "Waived"
        NOT_REQUIRED = "not_required", "Not required"

    class Source(models.TextChoices):
        UNIVERSITY_DATA = "university_data", "University data"
        USER_CREATED = "user_created", "Added by student"
        SYSTEM_GENERATED = "system_generated", "Generated checklist"

    application = models.ForeignKey(
        ApplicationTrackerItem, on_delete=models.CASCADE, related_name="requirements"
    )
    requirement_type = models.CharField(max_length=20, choices=RequirementType.choices)
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.MISSING)
    due_date = models.DateField(null=True, blank=True)
    is_required = models.BooleanField(default=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.USER_CREATED)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "due_date", "-created_at")
        indexes = [models.Index(fields=("application", "status"))]

    def __str__(self) -> str:
        return self.title


class ApplicationRecommendation(models.Model):
    class Status(models.TextChoices):
        NOT_REQUESTED = "not_requested", "Not requested"
        REQUESTED = "requested", "Requested"
        AGREED = "agreed", "Agreed"
        SUBMITTED = "submitted", "Submitted"
        UNAVAILABLE = "unavailable", "Unavailable"

    application = models.ForeignKey(
        ApplicationTrackerItem, on_delete=models.CASCADE, related_name="recommendation_requests"
    )
    recommender = models.ForeignKey(
        "user_profile_service.Recommender",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_requests",
    )
    recommender_name = models.CharField(max_length=150, blank=True)
    recommender_role = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_REQUESTED)
    request_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_date", "-created_at")
        indexes = [models.Index(fields=("application", "status"))]

    def __str__(self) -> str:
        return self.recommender_name or (self.recommender.name if self.recommender_id else "Recommender")


class ApplicationDocument(models.Model):
    class DocumentType(models.TextChoices):
        TRANSCRIPT = "transcript", "Transcript"
        PASSPORT = "passport", "Passport"
        CERTIFICATE = "certificate", "Certificate"
        TEST_REPORT = "test_report", "Test report"
        PORTFOLIO = "portfolio", "Portfolio"
        FINANCIAL_DOCUMENT = "financial_document", "Financial document"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        MISSING = "missing", "Missing"
        UPLOADED = "uploaded", "Uploaded"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    application = models.ForeignKey(
        ApplicationTrackerItem, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    title = models.CharField(max_length=240)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.MISSING)
    notes = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("application", "status"))]

    def __str__(self) -> str:
        return self.title

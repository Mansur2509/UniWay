from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Exam(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False, db_index=True)

    def __str__(self) -> str:
        return self.name


class ExamSection(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("exam", "slug"), name="unique_exam_section_slug")
        ]


class Question(models.Model):
    class Origin(models.TextChoices):
        ORIGINAL = "original", "Original UniWay content"
        LICENSED = "licensed", "Licensed content"

    section = models.ForeignKey(ExamSection, on_delete=models.CASCADE, related_name="questions")
    prompt = models.TextField()
    origin = models.CharField(max_length=20, choices=Origin.choices, default=Origin.ORIGINAL)
    provenance_note = models.CharField(max_length=240, default="Original UniWay demonstration content")
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answer_choices")
    label = models.CharField(max_length=5)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)


class Explanation(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="explanation")
    text = models.TextField()


class OfficialExamDate(models.Model):
    class ExamType(models.TextChoices):
        SAT = "SAT", "SAT"
        AP = "AP", "AP"

    class EventKind(models.TextChoices):
        EXAM = "exam", "Exam"
        ORDERING_DEADLINE = "ordering_deadline", "Ordering deadline"
        PERFORMANCE_TASK = "performance_task", "Performance task"
        PORTFOLIO_DEADLINE = "portfolio_deadline", "Portfolio deadline"

    class VerificationStatus(models.TextChoices):
        VERIFIED = "verified", "Verified"
        PARTIAL = "partial", "Partial"
        NOT_PUBLISHED = "not_published", "Not published"
        OUTDATED = "outdated", "Outdated"
        REQUIRES_REVIEW = "requires_review", "Requires review"

    exam_type = models.CharField(max_length=8, choices=ExamType.choices, db_index=True)
    name = models.CharField(max_length=160)
    event_kind = models.CharField(
        max_length=32, choices=EventKind.choices, default=EventKind.EXAM, db_index=True
    )
    test_date = models.DateField(null=True, blank=True)
    test_time = models.CharField(max_length=40, blank=True)
    registration_deadline = models.DateField(null=True, blank=True)
    late_registration_deadline = models.DateField(null=True, blank=True)
    late_test_date = models.DateField(null=True, blank=True)
    late_test_time = models.CharField(max_length=40, blank=True)
    score_release_window = models.CharField(max_length=160, blank=True)
    academic_year = models.CharField(max_length=20)
    exam_year = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    region = models.CharField(max_length=120, blank=True)
    source_url = models.URLField()
    source_title = models.CharField(max_length=240, blank=True)
    last_verified_date = models.DateField()
    last_verified_at = models.DateTimeField(null=True, blank=True)
    local_timezone = models.CharField(max_length=64, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PARTIAL,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("exam_year", "test_date", "exam_type")
        indexes = [
            models.Index(fields=("exam_type", "test_date")),
            models.Index(fields=("exam_type", "event_kind", "test_date")),
            models.Index(fields=("verification_status", "last_verified_date")),
        ]

    def clean(self):
        super().clean()
        if "collegeboard.org" not in self.source_url.lower():
            raise ValidationError(
                {"source_url": "SAT/AP date records must use an official College Board URL."}
            )
        if self.verification_status == self.VerificationStatus.VERIFIED and self.test_date is None:
            raise ValidationError({"test_date": "A verified exam date needs an exact date."})
        if (
            self.verification_status == self.VerificationStatus.NOT_PUBLISHED
            and self.test_date is not None
        ):
            raise ValidationError(
                {"test_date": "A not-published record cannot contain an exact date."}
            )
        if self.exam_year and self.test_date and self.exam_year != self.test_date.year:
            raise ValidationError({"exam_year": "Exam year must match the exact test date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def date_status(self) -> str:
        if self.test_date is None:
            return self.VerificationStatus.NOT_PUBLISHED
        if self.test_date < timezone.localdate():
            return self.VerificationStatus.OUTDATED
        if self.verification_status == self.VerificationStatus.VERIFIED:
            return self.VerificationStatus.VERIFIED
        if self.verification_status == self.VerificationStatus.OUTDATED:
            return self.VerificationStatus.OUTDATED
        return self.VerificationStatus.REQUIRES_REVIEW

    def __str__(self) -> str:
        return f"{self.exam_type} {self.name} ({self.test_date or self.exam_year or 'unpublished'})"

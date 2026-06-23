from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    class ScholarshipNeed(models.TextChoices):
        YES = "yes", "Yes"
        NO = "no", "No"
        UNSURE = "unsure", "Not sure"

    class EssayStatus(models.TextChoices):
        YES = "yes", "Yes"
        NO = "no", "No"
        NOT_YET = "not_yet", "Not yet"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    full_name = models.CharField(max_length=180, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, db_index=True)
    city = models.CharField(max_length=120, blank=True)
    school_or_university = models.CharField(max_length=240, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    expected_graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)
    education_status = models.CharField(max_length=120, blank=True)
    gpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gpa_scale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    intended_degree = models.CharField(max_length=120, blank=True)
    intended_major = models.CharField(max_length=180, blank=True)
    intended_majors = models.JSONField(default=list, blank=True)
    target_countries = models.JSONField(default=list, blank=True)
    target_universities = models.JSONField(default=list, blank=True)
    university_unsure = models.BooleanField(default=False)
    major_unsure = models.BooleanField(default=False)
    languages = models.JSONField(default=list, blank=True)
    test_scores = models.JSONField(default=dict, blank=True)
    exam_plans = models.JSONField(default=dict, blank=True)
    preparation_needs = models.JSONField(default=list, blank=True)
    activities = models.JSONField(default=dict, blank=True)
    essay_status = models.CharField(
        max_length=12,
        choices=EssayStatus.choices,
        default=EssayStatus.NOT_YET,
    )
    essay_stage = models.CharField(max_length=120, blank=True)
    support_priorities = models.JSONField(default=list, blank=True)
    telegram_username = models.CharField(max_length=33, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    scholarship_need = models.CharField(
        max_length=10,
        choices=ScholarshipNeed.choices,
        default=ScholarshipNeed.UNSURE,
    )
    sat_level = models.CharField(max_length=100, blank=True)
    ielts_level = models.CharField(max_length=100, blank=True)
    essay_level = models.CharField(max_length=100, blank=True)
    onboarding_sections = models.JSONField(default=list, blank=True)
    onboarding_version = models.PositiveSmallIntegerField(default=1)
    onboarding_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    interested_classes = models.JSONField(default=list, blank=True)
    ap_interests = models.JSONField(default=list, blank=True)
    activity_interests = models.JSONField(default=list, blank=True)
    career_interests = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)
    mun_debate_interest = models.BooleanField(default=False)
    research_interest = models.BooleanField(default=False)
    finance_literacy_interest = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

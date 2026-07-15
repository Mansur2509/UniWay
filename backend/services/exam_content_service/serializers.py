from django.utils import timezone
from rest_framework import serializers

from .models import (
    AnswerChoice,
    Exam,
    ExamSection,
    Explanation,
    OfficialExamDate,
    PracticeAnswer,
    PracticeSession,
    Question,
    QuestionBookmark,
    Skill,
    SkillMastery,
)


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ("id", "label", "text")


class ExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Explanation
        fields = ("text",)


class QuestionSerializer(serializers.ModelSerializer):
    answer_choices = AnswerChoiceSerializer(many=True, read_only=True)
    explanation = ExplanationSerializer(read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)
    exam_name = serializers.CharField(source="section.exam.name", read_only=True)

    class Meta:
        model = Question
        fields = "__all__"


class ExamSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSection
        fields = ("id", "name", "slug")


class ExamSerializer(serializers.ModelSerializer):
    sections = ExamSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = "__all__"


class OfficialExamDateSerializer(serializers.ModelSerializer):
    date_status = serializers.SerializerMethodField()
    countdown_days = serializers.SerializerMethodField()

    class Meta:
        model = OfficialExamDate
        fields = (
            "id",
            "exam_type",
            "event_kind",
            "name",
            "test_date",
            "test_time",
            "registration_deadline",
            "late_registration_deadline",
            "late_test_date",
            "late_test_time",
            "score_release_window",
            "academic_year",
            "exam_year",
            "region",
            "source_url",
            "source_title",
            "last_verified_date",
            "last_verified_at",
            "local_timezone",
            "verification_status",
            "date_status",
            "countdown_days",
            "notes",
        )

    def get_date_status(self, obj):
        return obj.date_status

    def get_countdown_days(self, obj):
        if obj.test_date is None or obj.test_date < timezone.localdate():
            return None
        return (obj.test_date - timezone.localdate()).days


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "slug")


class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        fields = ("id", "exam", "started_at", "completed_at", "is_timed", "time_limit_seconds")
        read_only_fields = ("id", "started_at", "completed_at")


class PracticeAnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()


class PracticeAnswerResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeAnswer
        fields = ("id", "question", "chosen_choice", "is_correct", "answered_at")


class SkillMasterySerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    accuracy_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = SkillMastery
        fields = ("id", "skill", "skill_name", "correct_count", "attempt_count", "accuracy_percent")


class QuestionBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBookmark
        fields = ("id", "question", "created_at")
        read_only_fields = ("id", "created_at")

from django.utils import timezone
from rest_framework import serializers

from .models import AnswerChoice, Exam, ExamSection, Explanation, OfficialExamDate, Question


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

from rest_framework import serializers

from .models import AnswerChoice, Exam, ExamSection, Explanation, Question


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


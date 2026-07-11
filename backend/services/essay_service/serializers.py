import re

from rest_framework import serializers

from services.university_service.models import UniversityFieldVerification

from .models import AIEssayScoreReport, EssayFeedback, EssayRevisionTask, EssayWorkspace

WORD_LIMIT_RE = re.compile(r"(?P<limit>\d{2,4})\s*(?:-|–)?\s*words?", re.IGNORECASE)


def _verified_word_limit(university) -> tuple[int | None, str]:
    if university is None or not university.essay_requirements:
        return None, ""
    verification = university.field_verifications.filter(
        field_name="essay_requirements",
        status=UniversityFieldVerification.Status.VERIFIED,
    ).first()
    if verification is None:
        return None, ""
    matches = [int(match.group("limit")) for match in WORD_LIMIT_RE.finditer(university.essay_requirements)]
    reasonable = [limit for limit in matches if 10 <= limit <= 2000]
    if not reasonable:
        return None, verification.source_url
    return max(reasonable), verification.source_url


class EssayRevisionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayRevisionTask
        fields = (
            "id",
            "essay",
            "title",
            "description",
            "category",
            "status",
            "created_at",
            "completed_at",
        )
        read_only_fields = ("id", "essay", "created_at", "completed_at")


class EssayRevisionTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayRevisionTask
        fields = ("title", "description", "category")

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value


class EssayFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayFeedback
        fields = (
            "id",
            "overall_label",
            "structure_score",
            "clarity_score",
            "authenticity_score",
            "specificity_score",
            "grammar_score",
            "prompt_fit_score",
            "word_count",
            "word_limit_status",
            "summary",
            "strengths",
            "issues",
            "revision_tasks",
            "created_at",
        )
        read_only_fields = fields


class EssayWorkspaceSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source="university.name", read_only=True, default=None)
    university_slug = serializers.CharField(source="university.slug", read_only=True, default=None)
    application_university_name = serializers.CharField(
        source="application.university.name", read_only=True, default=None
    )
    application_round = serializers.CharField(
        source="application.application_round", read_only=True, default=None
    )
    latest_feedback = serializers.SerializerMethodField()
    revision_tasks = serializers.SerializerMethodField()
    word_count = serializers.SerializerMethodField()

    class Meta:
        model = EssayWorkspace
        fields = (
            "id",
            "title",
            "essay_type",
            "university",
            "university_name",
            "university_slug",
            "application",
            "application_university_name",
            "application_round",
            "prompt_text",
            "word_limit",
            "draft_text",
            "status",
            "priority",
            "due_date",
            "prompt_verification_status",
            "prompt_confidence",
            "source_url",
            "notes",
            "suggestion_key",
            "last_reviewed_at",
            "latest_feedback",
            "revision_tasks",
            "word_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "suggestion_key",
            "last_reviewed_at",
            "created_at",
            "updated_at",
        )

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value

    def validate_application(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if request is None or value.user_id != request.user.id:
            raise serializers.ValidationError("You can only link your own applications.")
        return value

    def validate_word_limit(self, value):
        if value is None:
            return value
        if value < 10 or value > 2000:
            raise serializers.ValidationError("Word limit must be between 10 and 2000 words.")
        return value

    def validate(self, attrs):
        application = attrs.get("application")
        university = attrs.get("university")
        if application is not None:
            if university is not None and application.university_id != university.id:
                raise serializers.ValidationError(
                    {"university": "University must match the linked application."}
                )
            attrs["university"] = application.university
            university = application.university
        elif university is None and self.instance is not None:
            university = self.instance.university

        if attrs.get("word_limit") is None:
            verified_limit, source_url = _verified_word_limit(university)
            if verified_limit is not None:
                attrs["word_limit"] = verified_limit
                attrs["prompt_verification_status"] = EssayWorkspace.VerificationStatus.VERIFIED
                attrs["prompt_confidence"] = EssayWorkspace.Confidence.HIGH
                if source_url and not attrs.get("source_url"):
                    attrs["source_url"] = source_url
        return attrs

    def get_latest_feedback(self, obj):
        feedback = obj.feedback_entries.first()
        return EssayFeedbackSerializer(feedback).data if feedback else None

    def get_revision_tasks(self, obj):
        return EssayRevisionTaskSerializer(obj.revision_tasks.all(), many=True).data

    def get_word_count(self, obj):
        return len((obj.draft_text or "").split())


class EssayWorkspaceListSerializer(EssayWorkspaceSerializer):
    """List-view variant (PERFORMANCE-011 PART 4): drops `draft_text` from
    the payload. Essay cards on the list screen only need title/status/word
    count, not the full draft -- for essays with long drafts this meaningfully
    shrinks a response that returns every essay at once. `word_count` is
    unaffected since it's computed from the model instance already fetched by
    the queryset, not from this field list.
    """

    class Meta(EssayWorkspaceSerializer.Meta):
        fields = tuple(field for field in EssayWorkspaceSerializer.Meta.fields if field != "draft_text")


class AIEssayScoreReportSerializer(serializers.ModelSerializer):
    subscores = serializers.SerializerMethodField()
    nullable_scores = serializers.SerializerMethodField()

    class Meta:
        model = AIEssayScoreReport
        fields = (
            "id",
            "essay",
            "rubric_version",
            "overall_essay_readiness",
            "confidence",
            "verified_context_used",
            "subscores",
            "nullable_scores",
            "word_count",
            "word_limit_status",
            "ai_paraphrase_style_signal",
            "generic_language_signal",
            "unsupported_claims_signal",
            "strength_flags",
            "risk_flags",
            "approximate_suggestions",
            "source_warnings",
            "disclaimers",
            "biggest_strength",
            "biggest_weakness",
            "reflective_questions",
            "action_plan",
            "created_at",
        )
        read_only_fields = fields

    def get_subscores(self, obj):
        return {
            "prompt_fit": obj.prompt_fit,
            "structure": obj.structure,
            "specificity_evidence": obj.specificity_evidence,
            "authenticity": obj.authenticity,
            "language_clarity": obj.language_clarity,
            "word_limit_discipline": obj.word_limit_discipline,
            "school_program_alignment": obj.school_program_alignment,
        }

    def get_nullable_scores(self, obj):
        return {"school_program_alignment": obj.school_program_alignment}

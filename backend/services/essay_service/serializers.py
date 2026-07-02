from rest_framework import serializers

from .models import EssayFeedback, EssayRevisionTask, EssayWorkspace


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

    def validate(self, attrs):
        application = attrs.get("application")
        university = attrs.get("university")
        if application is not None:
            if university is not None and application.university_id != university.id:
                raise serializers.ValidationError(
                    {"university": "University must match the linked application."}
                )
            attrs["university"] = application.university
        return attrs

    def get_latest_feedback(self, obj):
        feedback = obj.feedback_entries.first()
        return EssayFeedbackSerializer(feedback).data if feedback else None

    def get_revision_tasks(self, obj):
        return EssayRevisionTaskSerializer(obj.revision_tasks.all(), many=True).data

    def get_word_count(self, obj):
        return len((obj.draft_text or "").split())

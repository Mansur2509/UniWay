from rest_framework import serializers

from .models import FeedbackReport, UserReport


class FeedbackReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackReport
        fields = ("id", "contact", "feedback_type", "page_module", "message", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_message(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()


class FeedbackReportAdminSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True, default=None)

    class Meta:
        model = FeedbackReport
        fields = (
            "id",
            "user",
            "user_email",
            "contact",
            "feedback_type",
            "page_module",
            "message",
            "status",
            "priority",
            "user_agent",
            "admin_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "user_email",
            "contact",
            "feedback_type",
            "page_module",
            "message",
            "user_agent",
            "created_at",
            "updated_at",
        )


class UserReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport
        fields = ("id", "target_type", "target_id", "reason", "description", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_reason(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Reason is required.")
        return value.strip()


class UserReportAdminSerializer(serializers.ModelSerializer):
    reporter_email = serializers.EmailField(source="reporter.email", read_only=True, default=None)

    class Meta:
        model = UserReport
        fields = (
            "id",
            "reporter",
            "reporter_email",
            "target_type",
            "target_id",
            "reason",
            "description",
            "status",
            "resolved_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "reporter",
            "reporter_email",
            "target_type",
            "target_id",
            "reason",
            "description",
            "resolved_at",
            "created_at",
        )

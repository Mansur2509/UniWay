from datetime import date, timedelta

from rest_framework import serializers

from .models import (
    ApplicationDocument,
    ApplicationMilestone,
    ApplicationRecommendation,
    ApplicationRequirement,
    ApplicationTrackerItem,
)


class ApplicationMilestoneSerializer(serializers.ModelSerializer):
    linked_roadmap_task_title = serializers.CharField(
        source="linked_roadmap_task.title", read_only=True, default=None
    )

    class Meta:
        model = ApplicationMilestone
        fields = (
            "id",
            "application",
            "title",
            "category",
            "due_date",
            "status",
            "priority",
            "notes",
            "linked_roadmap_task",
            "linked_roadmap_task_title",
            "source_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "application", "created_at", "updated_at")

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value


class ApplicationMilestoneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationMilestone
        fields = (
            "title",
            "category",
            "due_date",
            "priority",
            "notes",
            "linked_roadmap_task",
            "source_url",
        )

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value

    def validate_linked_roadmap_task(self, value):
        if value is not None:
            request = self.context.get("request")
            if request is None or value.user_id != request.user.id:
                raise serializers.ValidationError("You can only link your own roadmap tasks.")
        return value


class ApplicationRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationRequirement
        fields = (
            "id",
            "application",
            "requirement_type",
            "title",
            "description",
            "status",
            "due_date",
            "is_required",
            "source",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "application", "source", "created_at", "updated_at")


class ApplicationRequirementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationRequirement
        fields = (
            "requirement_type",
            "title",
            "description",
            "status",
            "due_date",
            "is_required",
            "order",
        )

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value


class ApplicationRecommendationSerializer(serializers.ModelSerializer):
    recommender_display_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationRecommendation
        fields = (
            "id",
            "application",
            "recommender",
            "recommender_name",
            "recommender_role",
            "recommender_display_name",
            "status",
            "request_date",
            "due_date",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "application", "created_at", "updated_at")

    def get_recommender_display_name(self, obj):
        if obj.recommender_id:
            return obj.recommender.name
        return obj.recommender_name or None

    def validate(self, attrs):
        recommender = attrs.get("recommender", getattr(self.instance, "recommender", None))
        recommender_name = attrs.get("recommender_name", getattr(self.instance, "recommender_name", ""))
        if not recommender and not recommender_name.strip():
            raise serializers.ValidationError(
                {"recommender_name": "Provide a recommender name or link an existing recommender."}
            )
        return attrs

    def validate_recommender(self, value):
        if value is not None:
            request = self.context.get("request")
            if request is None or value.user_id != request.user.id:
                raise serializers.ValidationError("You can only link your own recommenders.")
        return value


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = (
            "id",
            "application",
            "document_type",
            "title",
            "status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "application", "created_at", "updated_at")

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value


class ApplicationTrackerItemSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source="university.name", read_only=True)
    university_slug = serializers.CharField(source="university.slug", read_only=True)
    target_program_name = serializers.CharField(
        source="target_program.name", read_only=True, default=None
    )
    milestones = serializers.SerializerMethodField()
    checklist_progress = serializers.SerializerMethodField()
    official_deadline = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationTrackerItem
        fields = (
            "id",
            "university",
            "university_name",
            "university_slug",
            "target_program",
            "target_program_name",
            "application_round",
            "status",
            "priority",
            "fit_tier",
            "source",
            "deadline",
            "personal_estimated_deadline",
            "target_intake_year",
            "official_deadline",
            "financial_aid_deadline",
            "scholarship_deadline",
            "essays_status",
            "recommendations_status",
            "test_scores_status",
            "documents_status",
            "financial_aid_status",
            "notes",
            "archived_at",
            "milestones",
            "checklist_progress",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "fit_tier", "archived_at", "created_at", "updated_at")

    def validate(self, attrs):
        university = attrs.get("university", getattr(self.instance, "university", None))
        target_program = attrs.get(
            "target_program", getattr(self.instance, "target_program", None)
        )
        if target_program is not None and (
            university is None or target_program.university_id != university.id
        ):
            raise serializers.ValidationError(
                {"target_program": "Select a program offered by the chosen university."}
            )

        intake_year = attrs.get(
            "target_intake_year", getattr(self.instance, "target_intake_year", None)
        )
        if intake_year is not None and not date.today().year <= intake_year <= date.today().year + 8:
            raise serializers.ValidationError(
                {"target_intake_year": "Target intake year is outside the supported range."}
            )
        return attrs

    def get_milestones(self, obj):
        return ApplicationMilestoneSerializer(obj.milestones.all(), many=True).data

    def get_checklist_progress(self, obj):
        requirements = list(obj.requirements.all())
        if not requirements:
            return {"completed": 0, "total": 0, "percent": None}
        done_statuses = {
            ApplicationRequirement.Status.COMPLETED,
            ApplicationRequirement.Status.WAIVED,
            ApplicationRequirement.Status.NOT_REQUIRED,
        }
        completed = sum(1 for item in requirements if item.status in done_statuses)
        total = len(requirements)
        return {"completed": completed, "total": total, "percent": round(completed / total * 100)}

    def get_official_deadline(self, obj):
        university = obj.university
        raw_date = university.application_deadline
        verification = next(
            (
                item
                for item in university.field_verifications.all()
                if item.field_name == "application_deadline"
            ),
            None,
        )
        source_url = verification.source_url if verification else ""
        source = next(
            (
                item
                for item in university.data_sources.all()
                if source_url and item.source_url.rstrip("/") == source_url.rstrip("/")
            ),
            None,
        )
        payload = {
            "date": None,
            "source_date": raw_date.isoformat() if raw_date else None,
            "source_url": source_url,
            "source_title": source.source_title if source else "",
            "last_verified_date": (
                verification.last_verified_date.isoformat() if verification else None
            ),
            "intake_year": obj.target_intake_year,
            "round_type": obj.application_round,
            "timezone": "",
            "status": "not_published" if raw_date is None else "requires_review",
        }
        if raw_date is None:
            return payload

        # The imported single university deadline is explicitly the regular
        # decision value. Never relabel it as ED/EA/rolling.
        if obj.application_round != ApplicationTrackerItem.ApplicationRound.REGULAR_DECISION:
            return payload
        if obj.target_intake_year is None:
            return payload

        expected_year = (
            obj.target_intake_year - 1 if raw_date.month >= 8 else obj.target_intake_year
        )
        stale_source = bool(
            verification
            and verification.last_verified_date < date.today() - timedelta(days=400)
        )
        if raw_date.year != expected_year or stale_source:
            payload["status"] = "outdated"
            return payload
        if verification is None:
            return payload

        status_map = {
            "verified": "verified",
            "estimated": "estimated",
            "partial": "requires_review",
        }
        payload["status"] = status_map.get(verification.status, "requires_review")
        if payload["status"] in {"verified", "estimated"}:
            payload["date"] = raw_date.isoformat()
        return payload

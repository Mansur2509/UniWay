from rest_framework import serializers

from .budget import compare_cost_to_budget
from .import_jobs import MAX_IMPORT_UPLOAD_BYTES
from .major_matching import build_program_recommendation_summary
from .models import (
    SavedUniversity,
    University,
    UniversityDataSource,
    UniversityFieldVerification,
    UniversityImportJob,
    UniversityProgram,
    UniversityRequirement,
    UniversityScholarship,
    UniversitySubjectRanking,
)
from .program_display import format_program_display_names


class UniversityDataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityDataSource
        fields = "__all__"


class UniversityProgramSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    subject_rankings = serializers.SerializerMethodField()

    class Meta:
        model = UniversityProgram
        fields = (
            "id",
            "name",
            "display_name",
            "major_cluster",
            "degree_level",
            "department_or_school",
            "official_url",
            "source_url",
            "program_requirements_summary",
            "essay_requirements",
            "portfolio_required",
            "research_heavy",
            "stem_heavy",
            "interdisciplinary",
            "source_confidence",
            "last_verified_date",
            "subject_rankings",
        )

    def get_display_name(self, obj) -> str:
        return (format_program_display_names([obj.name]) or [obj.name])[0]

    def get_subject_rankings(self, obj):
        return UniversitySubjectRankingSerializer(obj.subject_rankings.all(), many=True).data


class UniversitySubjectRankingSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source="program.name", read_only=True, default=None)

    class Meta:
        model = UniversitySubjectRanking
        fields = (
            "id",
            "program",
            "program_name",
            "subject_area",
            "major_cluster",
            "rank",
            "source_name",
            "source_url",
            "ranking_year",
            "last_verified_date",
            "confidence",
            "notes",
        )


class UniversityRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityRequirement
        exclude = ("university",)


class UniversityScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityScholarship
        exclude = ("university",)


class UniversityFieldVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityFieldVerification
        fields = ("field_name", "status", "source_url", "last_verified_date", "note")


class UniversityShortlistMixin:
    def get_is_shortlisted(self, obj) -> bool:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        saved_ids = self.context.get("saved_university_ids")
        if saved_ids is not None:
            return obj.id in saved_ids
        return SavedUniversity.objects.filter(user=user, university=obj).exists()


class UniversityListSerializer(UniversityShortlistMixin, serializers.ModelSerializer):
    """Compact catalog-card payload.

    The detail serializer intentionally exposes nested public profile data, but
    a paginated catalog page only needs summary fields. Keeping this projection
    narrow prevents imported long-text/source records from making `/list` slow.
    """

    is_shortlisted = serializers.SerializerMethodField()
    majors_list = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = (
            "id",
            "name",
            "slug",
            "country",
            "city",
            "official_website",
            "summary",
            "institution_type",
            "is_published",
            "is_demo",
            "acceptance_rate",
            "gpa_average",
            "sat_average",
            "sat_p25",
            "sat_p50",
            "sat_p75",
            "ielts_minimum",
            "ielts_competitive",
            "test_policy",
            "tuition_amount",
            "tuition_currency",
            "tuition_original_amount",
            "tuition_original_currency",
            "tuition_usd_amount",
            "total_cost_original_amount",
            "total_cost_original_currency",
            "total_cost_usd_amount",
            "currency_conversion_confidence",
            "application_deadline",
            "scholarship_available",
            "qs_ranking",
            "qs_ranking_year",
            "global_rank",
            "the_rank",
            "national_rank",
            "ranking_source",
            "ranking_year",
            "ranking_confidence",
            "majors_list",
            "admissions_cycle_target",
            "is_shortlisted",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_majors_list(self, obj) -> list[str]:
        majors = obj.majors_list if isinstance(obj.majors_list, list) else []
        return majors[:8]


class UniversitySerializer(UniversityShortlistMixin, serializers.ModelSerializer):
    programs = UniversityProgramSerializer(many=True, read_only=True)
    program_display_names = serializers.SerializerMethodField()
    subject_rankings = UniversitySubjectRankingSerializer(many=True, read_only=True)
    program_matching = serializers.SerializerMethodField()
    requirements = UniversityRequirementSerializer(many=True, read_only=True)
    scholarships = UniversityScholarshipSerializer(many=True, read_only=True)
    data_sources = UniversityDataSourceSerializer(many=True, read_only=True)
    field_verifications = UniversityFieldVerificationSerializer(many=True, read_only=True)
    is_shortlisted = serializers.SerializerMethodField()
    budget_comparison = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_budget_comparison(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        profile = getattr(user, "student_profile", None)
        if profile is None:
            return None
        return compare_cost_to_budget(obj, profile)

    def get_program_display_names(self, obj) -> list[str]:
        # `.order_by()` builds a new queryset and bypasses Django's
        # prefetch_related cache for `programs`, forcing an extra query per
        # university; sorting the already-fetched list in Python reuses it.
        programs = sorted(obj.programs.all(), key=lambda program: program.id)
        return format_program_display_names(program.name for program in programs)

    def get_program_matching(self, obj):
        if not self.context.get("include_program_matching"):
            return None
        request = self.context.get("request")
        user = getattr(request, "user", None)
        profile = getattr(user, "student_profile", None) if user and user.is_authenticated else None
        if profile is None:
            return None
        return build_program_recommendation_summary(profile, obj)


class SavedUniversitySerializer(serializers.ModelSerializer):
    university = UniversitySerializer(read_only=True)

    class Meta:
        model = SavedUniversity
        fields = ("id", "university", "created_at")
        read_only_fields = ("id", "university", "created_at")


class ShortlistUniversitySummarySerializer(serializers.ModelSerializer):
    """Minimal university fields for dropdown/linking UI -- deliberately skips
    the full `UniversitySerializer`'s nested programs/rankings/requirements/
    scholarships/data_sources, which is expensive to serialize across an
    entire shortlist and unnecessary when the caller only needs a label.
    """

    class Meta:
        model = University
        fields = ("id", "slug", "name", "country", "city")
        read_only_fields = fields


class SavedUniversityLiteSerializer(serializers.ModelSerializer):
    university = ShortlistUniversitySummarySerializer(read_only=True)

    class Meta:
        model = SavedUniversity
        fields = ("id", "university", "created_at")
        read_only_fields = fields


class UniversityImportUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, uploaded_file):
        filename = uploaded_file.name or ""
        if not filename.lower().endswith(".xlsx"):
            raise serializers.ValidationError("Only .xlsx files are accepted.")
        if uploaded_file.size and uploaded_file.size > MAX_IMPORT_UPLOAD_BYTES:
            raise serializers.ValidationError("The workbook must be 10 MB or smaller.")
        return uploaded_file


class UniversityImportJobSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source="uploaded_by.email", read_only=True)

    class Meta:
        model = UniversityImportJob
        fields = (
            "id",
            "uploaded_by",
            "uploaded_by_email",
            "status",
            "mode",
            "original_filename",
            "row_count",
            "created_count",
            "updated_count",
            "skipped_count",
            "warning_count",
            "source_url_count",
            "field_verification_count",
            "parsed_deadline_count",
            "parsed_essay_count",
            "questionable_sat_count",
            "processed_count",
            "current_row",
            "current_university",
            "last_heartbeat_at",
            "summary_json",
            "error_message",
            "created_at",
            "started_at",
            "finished_at",
        )
        read_only_fields = fields

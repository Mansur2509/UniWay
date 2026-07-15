from rest_framework import serializers

from .models import Institution, InstitutionMembership


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ("id", "name", "slug", "country", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class InstitutionMembershipSerializer(serializers.ModelSerializer):
    institution_slug = serializers.CharField(source="institution.slug", read_only=True)

    class Meta:
        model = InstitutionMembership
        fields = (
            "id",
            "institution_slug",
            "role",
            "status",
            "shares_application_status",
            "shares_essays",
            "invited_at",
            "joined_at",
        )
        read_only_fields = ("id", "role", "status", "invited_at", "joined_at", "institution_slug")


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=[
            InstitutionMembership.MemberRole.STUDENT_MEMBER,
            InstitutionMembership.MemberRole.COUNSELOR,
        ]
    )


class ConsentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionMembership
        fields = ("shares_application_status", "shares_essays")


class StudentSummaryRowSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    full_name = serializers.CharField()
    shares_application_status = serializers.BooleanField()
    shares_essays = serializers.BooleanField()
    applications_by_status = serializers.DictField(allow_null=True)
    essay_count = serializers.IntegerField(allow_null=True)

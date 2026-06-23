from rest_framework import serializers

from .models import (
    University,
    UniversityDataSource,
    UniversityProgram,
    UniversityRequirement,
    UniversityScholarship,
)


class UniversityDataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityDataSource
        fields = "__all__"


class UniversityProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityProgram
        exclude = ("university",)


class UniversityRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityRequirement
        exclude = ("university",)


class UniversityScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityScholarship
        exclude = ("university",)


class UniversitySerializer(serializers.ModelSerializer):
    programs = UniversityProgramSerializer(many=True, read_only=True)
    requirements = UniversityRequirementSerializer(many=True, read_only=True)
    scholarships = UniversityScholarshipSerializer(many=True, read_only=True)
    data_sources = UniversityDataSourceSerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


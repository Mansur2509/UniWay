from django.contrib import admin

from .models import AIProfileAssessment


@admin.register(AIProfileAssessment)
class AIProfileAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "overall_profile_score",
        "confidence",
        "model_provider",
        "model_name",
        "is_stale",
        "created_at",
    )
    list_filter = ("confidence", "model_provider", "is_stale", "created_at")
    search_fields = ("user__email", "profile_snapshot_hash")
    readonly_fields = ("created_at",)

from django.contrib import admin

from .models import StudentProfile, UserPreference


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "country", "grade", "intended_degree", "updated_at")
    search_fields = (
        "user__email",
        "full_name",
        "city",
        "school_or_university",
        "intended_major",
    )


admin.site.register(UserPreference)

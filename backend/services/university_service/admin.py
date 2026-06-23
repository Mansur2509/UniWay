from django.contrib import admin

from .models import (
    University,
    UniversityDataSource,
    UniversityProgram,
    UniversityRequirement,
    UniversityScholarship,
)


class UniversityDataSourceInline(admin.TabularInline):
    model = UniversityDataSource
    extra = 0


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "city", "is_published", "updated_at")
    list_filter = ("country", "is_published")
    search_fields = ("name", "city")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [UniversityDataSourceInline]


admin.site.register(UniversityProgram)
admin.site.register(UniversityRequirement)
admin.site.register(UniversityScholarship)


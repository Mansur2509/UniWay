from django.contrib import admin

from .models import RoadmapPlan, RoadmapTask, RoadmapTaskDependency


class RoadmapTaskInline(admin.TabularInline):
    model = RoadmapTask
    extra = 0
    fields = ("title", "category", "priority", "status", "due_date")


@admin.register(RoadmapPlan)
class RoadmapPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "cycle_year", "active", "last_refreshed_at")
    list_filter = ("active", "cycle_year")
    search_fields = ("user__email", "title")
    inlines = [RoadmapTaskInline]


@admin.register(RoadmapTask)
class RoadmapTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "priority", "status", "due_date")
    list_filter = ("category", "priority", "status", "source_type")
    search_fields = ("title", "user__email")


admin.site.register(RoadmapTaskDependency)

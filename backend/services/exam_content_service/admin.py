from django.contrib import admin

from .models import AnswerChoice, Exam, ExamSection, Explanation, OfficialExamDate, Question

admin.site.register(Exam)
admin.site.register(ExamSection)
admin.site.register(Question)
admin.site.register(AnswerChoice)
admin.site.register(Explanation)


@admin.register(OfficialExamDate)
class OfficialExamDateAdmin(admin.ModelAdmin):
    list_display = (
        "exam_type",
        "name",
        "exam_year",
        "test_date",
        "verification_status",
        "effective_date_status",
        "last_verified_date",
    )
    list_filter = ("exam_type", "event_kind", "exam_year", "verification_status")
    search_fields = ("name", "source_title", "source_url")

    @admin.display(description="Current date status")
    def effective_date_status(self, obj):
        return obj.date_status

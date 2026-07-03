from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from common.permissions import IsAdminOrReadOnly

from .models import Exam, OfficialExamDate, Question
from .serializers import ExamSerializer, OfficialExamDateSerializer, QuestionSerializer


class ExamViewSet(ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("name",)

    def get_queryset(self):
        queryset = Exam.objects.prefetch_related("sections")
        if self.request.user.is_authenticated and self.request.user.is_admin_role:
            return queryset
        return queryset.filter(is_published=True)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticated()]
        return super().get_permissions()


class QuestionViewSet(ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ("section__exam__slug", "section__slug")
    queryset = Question.objects.filter(
        is_published=True,
        section__exam__is_published=True,
    ).select_related("section", "section__exam", "explanation").prefetch_related("answer_choices")


class OfficialExamDateViewSet(ReadOnlyModelViewSet):
    serializer_class = OfficialExamDateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ("exam_type", "event_kind", "academic_year", "verification_status")
    ordering_fields = ("test_date", "registration_deadline", "late_registration_deadline")

    def get_queryset(self):
        return OfficialExamDate.objects.all().order_by("test_date", "exam_type", "name")

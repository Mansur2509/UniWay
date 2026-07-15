from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from common.permissions import IsAdminOrReadOnly

from .models import (
    AnswerChoice,
    Exam,
    OfficialExamDate,
    PracticeAnswer,
    PracticeSession,
    Question,
    QuestionBookmark,
    SkillMastery,
)
from .serializers import (
    ExamSerializer,
    OfficialExamDateSerializer,
    PracticeAnswerResultSerializer,
    PracticeAnswerSubmitSerializer,
    PracticeSessionSerializer,
    QuestionBookmarkSerializer,
    QuestionSerializer,
    SkillMasterySerializer,
)


class ExamViewSet(ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("name",)

    def get_queryset(self):
        queryset = Exam.objects.prefetch_related("sections").order_by("name", "id")
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
    ).select_related("section", "section__exam", "explanation").prefetch_related(
        "answer_choices"
    ).order_by("section__exam__slug", "section__slug", "id")


class OfficialExamDateViewSet(ReadOnlyModelViewSet):
    serializer_class = OfficialExamDateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = (
        "exam_type",
        "event_kind",
        "academic_year",
        "exam_year",
        "verification_status",
    )
    ordering_fields = ("test_date", "registration_deadline", "late_registration_deadline")

    def get_queryset(self):
        queryset = OfficialExamDate.objects.all()
        if self.request.query_params.get("include_past") != "true":
            queryset = queryset.filter(
                Q(test_date__gte=timezone.now().date()) | Q(test_date__isnull=True)
            )
        return queryset.order_by(
            "exam_year",
            F("test_date").asc(nulls_last=True),
            "exam_type",
            "name",
        )


class PracticeSessionViewSet(ModelViewSet):
    """POST-V1-021 Phase 7. Always scoped to `request.user` -- a student
    can only ever see, answer within, or complete their own sessions."""

    serializer_class = PracticeSessionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).order_by("-started_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def answer(self, request, pk=None):
        session = self.get_object()
        if session.completed_at is not None:
            return Response(
                {"detail": "This session is already complete."}, status=status.HTTP_409_CONFLICT
            )
        serializer = PracticeAnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = get_object_or_404(
            Question, pk=serializer.validated_data["question_id"], is_published=True
        )
        choice = get_object_or_404(
            AnswerChoice, pk=serializer.validated_data["choice_id"], question=question
        )

        answer, _ = PracticeAnswer.objects.update_or_create(
            session=session,
            question=question,
            defaults={"chosen_choice": choice, "is_correct": choice.is_correct},
        )

        if question.skill_id:
            mastery, _ = SkillMastery.objects.get_or_create(
                user=request.user, skill_id=question.skill_id
            )
            mastery.attempt_count += 1
            if choice.is_correct:
                mastery.correct_count += 1
            mastery.save(update_fields=["attempt_count", "correct_count", "updated_at"])

        return Response(PracticeAnswerResultSerializer(answer).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        session = self.get_object()
        if session.completed_at is None:
            session.completed_at = timezone.now()
            session.save(update_fields=["completed_at"])
        return Response(PracticeSessionSerializer(session).data)


class SkillMasteryListView(ReadOnlyModelViewSet):
    serializer_class = SkillMasterySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return SkillMastery.objects.filter(user=self.request.user).select_related("skill")


class QuestionBookmarkViewSet(CreateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = QuestionBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuestionBookmark.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        # Idempotent: bookmarking an already-bookmarked question is a no-op,
        # not a duplicate row or a 400.
        question = serializer.validated_data["question"]
        QuestionBookmark.objects.get_or_create(user=self.request.user, question=question)

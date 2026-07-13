from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.activity_service.models import AnalyticsEvent
from services.activity_service.services import track_event
from services.exam_content_service.models import OfficialExamDate

from .models import RoadmapPlan, RoadmapTask
from .roadmap_generator import generate_roadmap
from .serializers import (
    ExamPlanRoadmapTaskCreateSerializer,
    RoadmapPlanSerializer,
    RoadmapTaskCreateSerializer,
    RoadmapTaskSerializer,
)


class RoadmapPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan = (
            RoadmapPlan.objects.filter(user=request.user, active=True)
            .order_by("-generated_at")
            .first()
        )
        if plan is None:
            return Response({"detail": "No roadmap has been generated yet.", "plan": None})
        serializer = RoadmapPlanSerializer(plan, context={"request": request})
        return Response({"detail": "", "plan": serializer.data})


class GenerateRoadmapView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan, warnings = generate_roadmap(request.user)
        serializer = RoadmapPlanSerializer(plan, context={"request": request})
        track_event(user=request.user, event_type=AnalyticsEvent.EventType.ROADMAP_GENERATED)
        return Response({"plan": serializer.data, "missing_data_warnings": warnings})


class RoadmapTaskViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RoadmapTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = (
        "status",
        "category",
        "priority",
        "linked_university",
        "linked_application",
        "source_type",
    )

    def get_queryset(self):
        queryset = RoadmapTask.objects.filter(user=self.request.user).select_related(
            "linked_university",
            "linked_application__university",
            "linked_event",
        )
        params = self.request.query_params
        due_before = params.get("due_before")
        due_after = params.get("due_after")
        exam = (params.get("exam") or "").strip()
        task_kind = (params.get("task_kind") or "").strip()
        view = (params.get("view") or "").strip()
        if due_before:
            queryset = queryset.filter(due_date__lte=due_before)
        if due_after:
            queryset = queryset.filter(due_date__gte=due_after)
        if exam:
            queryset = queryset.filter(category=RoadmapTask.Category.EXAMS).filter(
                Q(title__icontains=exam)
                | Q(description__icontains=exam)
                | Q(generated_reason__icontains=exam)
                | Q(evidence_note__icontains=exam)
            )
        if task_kind == "manual":
            queryset = queryset.filter(source_type=RoadmapTask.SourceType.MANUAL)
        elif task_kind == "generated":
            queryset = queryset.exclude(source_type=RoadmapTask.SourceType.MANUAL)

        timeline_marker_query = Q(
            source_type=RoadmapTask.SourceType.UNIVERSITY_DEADLINE,
            dedup_key__startswith="university_deadline:",
        ) & (
            Q(dedup_key__endswith=":60")
            | Q(dedup_key__endswith=":30")
            | Q(dedup_key__endswith=":15")
            | Q(dedup_key__endswith=":14")
            | Q(dedup_key__endswith=":7")
        )
        if view == "list":
            queryset = queryset.exclude(timeline_marker_query)
        elif view == "timeline":
            queryset = queryset.filter(Q(due_date__isnull=False) | timeline_marker_query)
        return queryset.order_by("status", "due_date", "-priority", "created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return RoadmapTaskCreateSerializer
        return RoadmapTaskSerializer

    def perform_create(self, serializer):
        plan, _ = RoadmapPlan.objects.get_or_create(
            user=self.request.user, active=True, defaults={"title": "My admissions roadmap"}
        )
        serializer.save(
            user=self.request.user,
            plan=plan,
            source_type=RoadmapTask.SourceType.MANUAL,
        )

    def perform_update(self, serializer):
        previous_status = serializer.instance.status
        task = serializer.save()
        if (
            task.status == RoadmapTask.Status.COMPLETED
            and previous_status != RoadmapTask.Status.COMPLETED
        ):
            track_event(
                user=self.request.user,
                event_type=AnalyticsEvent.EventType.ROADMAP_TASK_COMPLETED,
                entity_type="roadmap_task",
                entity_id=task.id,
                metadata={"category": task.category},
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        full_serializer = RoadmapTaskSerializer(
            serializer.instance, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(full_serializer.data)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.source_type != RoadmapTask.SourceType.MANUAL:
            return Response(
                {"detail": "Generated tasks cannot be deleted. Skip the task instead."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="from-exam-plan")
    def from_exam_plan(self, request):
        input_serializer = ExamPlanRoadmapTaskCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        official_date = get_object_or_404(
            OfficialExamDate,
            pk=input_serializer.validated_data["official_exam_date_id"],
        )
        if (
            official_date.verification_status
            != OfficialExamDate.VerificationStatus.VERIFIED
            or official_date.test_date is None
            or official_date.test_date < timezone.now().date()
        ):
            return Response(
                {"detail": "Only a verified upcoming official exam date can be added."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            plan, _ = RoadmapPlan.objects.get_or_create(
                user=request.user,
                active=True,
                defaults={"title": "My admissions roadmap"},
            )
            plan = RoadmapPlan.objects.select_for_update().get(pk=plan.pk)
            task, created = RoadmapTask.objects.get_or_create(
                user=request.user,
                plan=plan,
                dedup_key=f"official_exam_date:{official_date.id}",
                defaults={
                    "title": input_serializer.validated_data["title"],
                    "description": input_serializer.validated_data.get("description", ""),
                    "category": RoadmapTask.Category.EXAMS,
                    "priority": RoadmapTask.Priority.HIGH,
                    "due_date": official_date.test_date,
                    "source_type": RoadmapTask.SourceType.EXAM_PLAN,
                    "evidence_note": official_date.source_title,
                    "source_url": official_date.source_url,
                },
            )
        output = RoadmapTaskSerializer(task, context={"request": request})
        return Response(
            output.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = RoadmapTask.Status.COMPLETED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(RoadmapTaskSerializer(task, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="skip")
    def skip(self, request, pk=None):
        task = self.get_object()
        task.status = RoadmapTask.Status.SKIPPED
        task.save(update_fields=["status", "updated_at"])
        return Response(RoadmapTaskSerializer(task, context={"request": request}).data)

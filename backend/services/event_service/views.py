from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from common.permissions import IsAdminOrReadOnly, IsAdminRole, IsOrganizerOrAdmin

from .models import Event, EventCategory, EventRegistration
from .serializers import (
    EventCategorySerializer,
    EventModerationLogSerializer,
    EventRegistrationSerializer,
    EventRejectionSerializer,
    EventSerializer,
    OrganizerEventSerializer,
    OrganizerParticipantSerializer,
    PublicEventSerializer,
)
from .services import (
    ACTIVE_REGISTRATION_STATUSES,
    approve_event,
    archive_event,
    cancel_event_registration,
    cancel_owned_event,
    public_event_queryset,
    register_for_event,
    reject_event,
    submit_event_for_review,
    validate_event_is_editable,
)


class PublicEventListView(generics.ListAPIView):
    serializer_class = PublicEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = public_event_queryset()
        params = self.request.query_params
        search = params.get("search", "").strip()
        category = params.get("category", "").strip()
        country = params.get("country", "").strip()
        city = params.get("city", "").strip()
        price_type = params.get("price_type", "").strip()
        event_format = params.get("format", "").strip()
        is_online = params.get("is_online", "").strip().lower()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(short_description__icontains=search)
                | Q(description__icontains=search)
                | Q(organizer_name__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__slug=category)
        if country:
            queryset = queryset.filter(location__country__iexact=country)
        if city:
            queryset = queryset.filter(location__city__iexact=city)
        if price_type:
            queryset = queryset.filter(price_type=price_type)
        if event_format:
            queryset = queryset.filter(format=event_format)
        if is_online in {"true", "false"}:
            queryset = queryset.filter(is_online=is_online == "true")
        return queryset.order_by("starts_at")


class PublicEventDetailView(generics.RetrieveAPIView):
    serializer_class = PublicEventSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        return public_event_queryset()


class EventRegistrationView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_registration"

    def post(self, request, slug):
        event = get_object_or_404(Event.objects.all(), slug=slug)
        registration, created = register_for_event(event=event, user=request.user)
        serializer = EventRegistrationSerializer(
            registration,
            context={"request": request},
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class EventRegistrationCancelView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_registration"

    def post(self, request, slug):
        event = get_object_or_404(Event.objects.all(), slug=slug)
        registration = cancel_event_registration(event=event, user=request.user)
        return Response(
            EventRegistrationSerializer(
                registration,
                context={"request": request},
            ).data
        )

    def delete(self, request, slug):
        return self.post(request, slug)


class MyEventRegistrationListView(generics.ListAPIView):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            EventRegistration.objects.filter(
                user=self.request.user,
                status__in=ACTIVE_REGISTRATION_STATUSES,
            )
            .select_related(
                "event",
                "event__category",
                "event__location",
                "event__source",
                "event__organizer",
            )
            .order_by("event__starts_at")
        )


def organizer_event_queryset(user):
    queryset = Event.objects.select_related(
        "category",
        "location",
        "source",
        "organizer",
    ).prefetch_related("moderation_logs")
    if user.is_admin_role:
        return queryset
    return queryset.filter(organizer=user)


class OrganizerCategoryListView(generics.ListAPIView):
    serializer_class = EventCategorySerializer
    permission_classes = [IsOrganizerOrAdmin]
    pagination_class = None
    queryset = EventCategory.objects.order_by("name")


class OrganizerEventListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsOrganizerOrAdmin]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_submission"

    def get_queryset(self):
        return organizer_event_queryset(self.request.user).order_by("-updated_at")


class OrganizerEventDetailView(generics.GenericAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsOrganizerOrAdmin]
    lookup_field = "slug"
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_submission"

    def get_queryset(self):
        return organizer_event_queryset(self.request.user)

    def get(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    def patch(self, request, *args, **kwargs):
        event = self.get_object()
        validate_event_is_editable(event)
        serializer = self.get_serializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class OrganizerEventSubmitView(generics.GenericAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsOrganizerOrAdmin]
    lookup_field = "slug"
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_submission"

    def get_queryset(self):
        return organizer_event_queryset(self.request.user)

    def post(self, request, *args, **kwargs):
        event = submit_event_for_review(
            event=self.get_object(),
            actor=request.user,
        )
        return Response(self.get_serializer(event).data)


class OrganizerEventRegistrationListView(generics.ListAPIView):
    serializer_class = OrganizerParticipantSerializer
    permission_classes = [IsOrganizerOrAdmin]

    def get_event(self):
        event = get_object_or_404(
            organizer_event_queryset(self.request.user),
            slug=self.kwargs["slug"],
        )
        if event.moderation_status != Event.Status.PUBLISHED:
            raise ValidationError(
                {"status": "Participants are available only for published events."}
            )
        return event

    def get_queryset(self):
        return EventRegistration.objects.filter(
            event=self.get_event(),
        ).order_by("-created_at")


class OrganizerEventArchiveView(generics.GenericAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsOrganizerOrAdmin]
    lookup_field = "slug"
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_submission"

    def get_queryset(self):
        return organizer_event_queryset(self.request.user)

    def post(self, request, *args, **kwargs):
        event = archive_event(
            event=self.get_object(),
            actor=request.user,
            is_admin=False,
        )
        return Response(self.get_serializer(event).data)


class OrganizerEventCancelView(generics.GenericAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsOrganizerOrAdmin]
    lookup_field = "slug"
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_submission"

    def get_queryset(self):
        return organizer_event_queryset(self.request.user)

    def post(self, request, *args, **kwargs):
        event = cancel_owned_event(
            event=self.get_object(),
            actor=request.user,
        )
        return Response(self.get_serializer(event).data)


class PendingEventModerationListView(generics.ListAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return (
            Event.objects.filter(moderation_status=Event.Status.PENDING_REVIEW)
            .select_related("category", "location", "source", "organizer")
            .prefetch_related("moderation_logs")
            .order_by("updated_at")
        )


class AdminEventActionView(generics.GenericAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsAdminRole]
    lookup_field = "slug"
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_moderation"
    queryset = Event.objects.select_related(
        "category",
        "location",
        "source",
        "organizer",
    ).prefetch_related("moderation_logs")


class AdminEventApproveView(AdminEventActionView):
    def post(self, request, *args, **kwargs):
        event = approve_event(event=self.get_object(), actor=request.user)
        return Response(self.get_serializer(event).data)


class AdminEventRejectView(AdminEventActionView):
    def post(self, request, *args, **kwargs):
        rejection = EventRejectionSerializer(data=request.data)
        rejection.is_valid(raise_exception=True)
        event = reject_event(
            event=self.get_object(),
            actor=request.user,
            reason=rejection.validated_data["reason"],
        )
        return Response(self.get_serializer(event).data)


class AdminEventArchiveView(AdminEventActionView):
    def post(self, request, *args, **kwargs):
        event = archive_event(
            event=self.get_object(),
            actor=request.user,
            is_admin=True,
        )
        return Response(self.get_serializer(event).data)


class AdminEventModerationLogListView(generics.ListAPIView):
    serializer_class = EventModerationLogSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None

    def get_queryset(self):
        event = get_object_or_404(Event, slug=self.kwargs["slug"])
        return event.moderation_logs.select_related("moderator").order_by("-created_at")


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    search_fields = ("title", "description", "organizer_name", "location__city")
    filterset_fields = (
        "category__slug",
        "format",
        "is_free",
        "price_type",
        "scholarship_available",
        "language",
        "location__country",
        "location__city",
    )
    ordering_fields = ("starts_at", "deadline", "created_at")

    def get_queryset(self):
        queryset = Event.objects.select_related("category", "location", "source", "organizer")
        user = self.request.user
        if user.is_authenticated and user.is_admin_role:
            return queryset
        if user.is_authenticated and user.is_organizer and self.action not in {"list", "retrieve"}:
            return queryset.filter(organizer=user)

        queryset = queryset.filter(
            moderation_status=Event.Status.PUBLISHED,
            visibility=Event.Visibility.PUBLIC,
        )
        deadline_before = parse_datetime(self.request.query_params.get("deadline_before", ""))
        deadline_after = parse_datetime(self.request.query_params.get("deadline_after", ""))
        if deadline_before:
            queryset = queryset.filter(deadline__lte=deadline_before)
        if deadline_after:
            queryset = queryset.filter(deadline__gte=deadline_after)
        return queryset

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticated()]
        if self.action == "create":
            return [IsOrganizerOrAdmin()]
        return [IsAdminOrReadOnly()]

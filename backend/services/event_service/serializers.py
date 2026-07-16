from django.db import transaction
from rest_framework import serializers

from .models import (
    Event,
    EventCategory,
    EventFormField,
    EventLocation,
    EventModerationLog,
    EventNotification,
    EventRegistration,
    EventRegistrationAnswer,
    EventSource,
    EventSubmission,
    EventTicket,
    OrganizerApplication,
    OrganizerModeration,
    ParticipationRecord,
)
from .services import (
    ACTIVE_REGISTRATION_STATUSES,
    ORGANIZER_EDITABLE_STATUSES,
    event_infrastructure_tables_available,
    generate_unique_event_slug,
)


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ("name", "slug")


class EventLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLocation
        exclude = ("event",)


class EventSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSource
        exclude = ("event",)


class EventFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFormField
        fields = (
            "id",
            "field_type",
            "label",
            "help_text",
            "is_required",
            "order",
            "choices",
            "validation",
        )
        read_only_fields = ("id", "order")


class EventTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTicket
        fields = (
            "code",
            "status",
            "created_at",
            "checked_in_at",
            "expires_at",
        )
        read_only_fields = fields


class EventRegistrationAnswerSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField(source="field.id", read_only=True)
    field_label = serializers.CharField(source="field.label", read_only=True)
    field_type = serializers.CharField(source="field.field_type", read_only=True)

    class Meta:
        model = EventRegistrationAnswer
        fields = (
            "field_id",
            "field_label",
            "field_type",
            "value",
            "created_at",
        )
        read_only_fields = fields


class ParticipationRecordSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    event_slug = serializers.CharField(source="event.slug", read_only=True)
    organizer_name = serializers.CharField(source="event.organizer_name", read_only=True)
    starts_at = serializers.DateTimeField(source="event.starts_at", read_only=True)

    class Meta:
        model = ParticipationRecord
        fields = (
            "id",
            "event_title",
            "event_slug",
            "organizer_name",
            "attendance_status",
            "participation_type",
            "verification_status",
            "verified_at",
            "record_id",
            "public_verification_code",
            "starts_at",
            "created_at",
        )
        read_only_fields = fields


class EventNotificationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    event_slug = serializers.CharField(source="event.slug", read_only=True)

    class Meta:
        model = EventNotification
        fields = (
            "id",
            "notification_type",
            "channel",
            "status",
            "payload",
            "event_title",
            "event_slug",
            "created_at",
        )
        read_only_fields = fields


class PublicEventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    location = EventLocationSerializer(read_only=True)
    source = EventSourceSerializer(read_only=True)
    status = serializers.CharField(source="moderation_status", read_only=True)
    start_at = serializers.DateTimeField(source="starts_at", read_only=True)
    end_at = serializers.DateTimeField(source="ends_at", read_only=True)
    registration_deadline = serializers.DateTimeField(source="deadline", read_only=True)
    registration_count = serializers.SerializerMethodField()
    spots_left = serializers.SerializerMethodField()
    registration_status = serializers.SerializerMethodField()
    registration_form_fields = serializers.SerializerMethodField()
    registration_ticket = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "category",
            "organizer_name",
            "location",
            "is_online",
            "online_url",
            "format",
            "start_at",
            "end_at",
            "registration_deadline",
            "capacity",
            "registration_count",
            "spots_left",
            "price_type",
            "price_amount",
            "currency",
            "status",
            "visibility",
            "cover_image_url",
            "language",
            "eligibility",
            "scholarship_available",
            "source",
            "registration_status",
            "registration_form_fields",
            "registration_ticket",
        )

    def get_registration_count(self, obj):
        annotated_count = getattr(obj, "active_registration_count", None)
        if annotated_count is not None:
            return annotated_count
        return obj.registrations.filter(
            status__in=(
                EventRegistration.Status.REGISTERED,
                EventRegistration.Status.ATTENDED,
            )
        ).count()

    def get_spots_left(self, obj):
        if obj.capacity is None:
            return None
        return max(obj.capacity - self.get_registration_count(obj), 0)

    def get_registration_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        prefetched = getattr(obj, "current_user_registrations", None)
        if prefetched is not None:
            return prefetched[0].status if prefetched else None
        registration = (
            obj.registrations.filter(
                user=request.user,
                status__in=ACTIVE_REGISTRATION_STATUSES,
            )
            .order_by("-updated_at")
            .first()
        )
        return registration.status if registration else None

    def _current_registration(self, obj):
        if not event_infrastructure_tables_available():
            return None
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        prefetched = getattr(obj, "current_user_registrations", None)
        if prefetched is not None:
            return prefetched[0] if prefetched else None
        return (
            obj.registrations.filter(
                user=request.user,
                status__in=ACTIVE_REGISTRATION_STATUSES,
            )
            .select_related("ticket")
            .order_by("-updated_at")
            .first()
        )

    def get_registration_form_fields(self, obj):
        if not self.context.get("include_event_registration_extras"):
            return []
        if not event_infrastructure_tables_available():
            return []
        fields = obj.form_fields.all().order_by("order", "id")
        return EventFormFieldSerializer(fields, many=True).data

    def get_registration_ticket(self, obj):
        if not self.context.get("include_event_registration_extras"):
            return None
        registration = self._current_registration(obj)
        if not registration or not hasattr(registration, "ticket"):
            return None
        return EventTicketSerializer(registration.ticket).data


class EventRegistrationSerializer(serializers.ModelSerializer):
    event = PublicEventSerializer(read_only=True)
    ticket = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = EventRegistration
        fields = (
            "id",
            "event",
            "status",
            "payment_status",
            "registration_data",
            "contact_snapshot",
            "ticket",
            "answers",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_ticket(self, obj):
        if not self.context.get("include_event_registration_extras"):
            return None
        if not event_infrastructure_tables_available():
            return None
        if not hasattr(obj, "ticket"):
            return None
        return EventTicketSerializer(obj.ticket).data

    def get_answers(self, obj):
        if not self.context.get("include_event_registration_extras"):
            return []
        if not event_infrastructure_tables_available():
            return []
        return EventRegistrationAnswerSerializer(obj.answers.all(), many=True).data


class OrganizerEventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    category_slug = serializers.SlugRelatedField(
        source="category",
        slug_field="slug",
        queryset=EventCategory.objects.all(),
        write_only=True,
    )
    location = EventLocationSerializer()
    source = EventSourceSerializer()
    status = serializers.CharField(source="moderation_status", read_only=True)
    start_at = serializers.DateTimeField(source="starts_at")
    end_at = serializers.DateTimeField(
        source="ends_at",
        allow_null=True,
        required=False,
    )
    registration_deadline = serializers.DateTimeField(
        source="deadline",
        allow_null=True,
        required=False,
    )
    organizer_email = serializers.EmailField(source="organizer.email", read_only=True)
    moderation_note = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_submit = serializers.SerializerMethodField()
    can_view_participants = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "category",
            "category_slug",
            "organizer_name",
            "organizer_email",
            "format",
            "is_online",
            "online_url",
            "start_at",
            "end_at",
            "registration_deadline",
            "capacity",
            "price_type",
            "price_amount",
            "currency",
            "visibility",
            "cover_image_url",
            "language",
            "eligibility",
            "scholarship_available",
            "location",
            "source",
            "status",
            "moderation_note",
            "can_edit",
            "can_submit",
            "can_view_participants",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "organizer_email",
            "status",
            "moderation_note",
            "can_edit",
            "can_submit",
            "can_view_participants",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        deadline = attrs.get("deadline", getattr(self.instance, "deadline", None))
        price_type = attrs.get(
            "price_type",
            getattr(self.instance, "price_type", Event.PriceType.UNKNOWN),
        )
        price_amount = attrs.get(
            "price_amount",
            getattr(self.instance, "price_amount", None),
        )
        currency = attrs.get("currency", getattr(self.instance, "currency", ""))
        event_format = attrs.get("format", getattr(self.instance, "format", None))
        is_online = attrs.get(
            "is_online",
            event_format in {Event.Format.ONLINE, Event.Format.HYBRID},
        )
        online_url = attrs.get("online_url", getattr(self.instance, "online_url", ""))

        if ends_at and starts_at and ends_at <= starts_at:
            raise serializers.ValidationError(
                {"end_at": "End time must be after start time."}
            )
        if deadline and starts_at and deadline > starts_at:
            raise serializers.ValidationError(
                {"registration_deadline": "Deadline cannot be after the event starts."}
            )
        if price_type == Event.PriceType.PAID and price_amount is None:
            raise serializers.ValidationError(
                {"price_amount": "Paid events require a price amount."}
            )
        if price_amount is not None and price_amount < 0:
            raise serializers.ValidationError(
                {"price_amount": "Price cannot be negative."}
            )
        if price_amount is not None and not currency:
            raise serializers.ValidationError(
                {"currency": "Priced events require a currency."}
            )
        if currency and len(currency) != 3:
            raise serializers.ValidationError(
                {"currency": "Use a three-letter currency code."}
            )
        if is_online and not online_url:
            raise serializers.ValidationError(
                {"online_url": "Online and hybrid events require an online URL."}
            )

        attrs["is_online"] = event_format in {
            Event.Format.ONLINE,
            Event.Format.HYBRID,
        }
        attrs["is_free"] = price_type == Event.PriceType.FREE
        if currency:
            attrs["currency"] = currency.upper()
        if price_type == Event.PriceType.FREE:
            attrs["price_amount"] = None
            attrs["currency"] = ""
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        location_data = validated_data.pop("location")
        source_data = validated_data.pop("source")
        event = Event.objects.create(
            organizer=self.context["request"].user,
            slug=generate_unique_event_slug(validated_data["title"]),
            moderation_status=Event.Status.DRAFT,
            **validated_data,
        )
        EventLocation.objects.create(event=event, **location_data)
        EventSource.objects.create(event=event, **source_data)
        return event

    @transaction.atomic
    def update(self, instance, validated_data):
        location_data = validated_data.pop("location", None)
        source_data = validated_data.pop("source", None)
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()
        if location_data is not None:
            EventLocation.objects.update_or_create(event=instance, defaults=location_data)
        if source_data is not None:
            EventSource.objects.update_or_create(event=instance, defaults=source_data)
        return instance

    def get_moderation_note(self, obj):
        if obj.moderation_status != Event.Status.REJECTED:
            return ""
        latest_log = obj.moderation_logs.filter(
            new_status=Event.Status.REJECTED
        ).order_by("-created_at").first()
        return latest_log.note if latest_log else ""

    def get_can_edit(self, obj):
        return obj.moderation_status in ORGANIZER_EDITABLE_STATUSES

    def get_can_submit(self, obj):
        return obj.moderation_status in (
            Event.Status.DRAFT,
            Event.Status.REJECTED,
        )

    def get_can_view_participants(self, obj):
        return obj.moderation_status == Event.Status.PUBLISHED


class EventModerationLogSerializer(serializers.ModelSerializer):
    moderator_email = serializers.EmailField(source="moderator.email", read_only=True)

    class Meta:
        model = EventModerationLog
        fields = (
            "id",
            "previous_status",
            "new_status",
            "note",
            "moderator_email",
            "created_at",
        )
        read_only_fields = fields


class OrganizerParticipantSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    telegram_username = serializers.SerializerMethodField()
    ticket_status = serializers.SerializerMethodField()
    checked_in_at = serializers.SerializerMethodField()
    participation_verified = serializers.SerializerMethodField()
    answers = EventRegistrationAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = EventRegistration
        fields = (
            "id",
            "full_name",
            "email",
            "telegram_username",
            "status",
            "payment_status",
            "ticket_status",
            "checked_in_at",
            "participation_verified",
            "answers",
            "created_at",
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.registration_data.get("full_name", "")

    def get_email(self, obj):
        return obj.contact_snapshot.get("email", "")

    def get_telegram_username(self, obj):
        return obj.contact_snapshot.get("telegram_username", "")

    def get_ticket_status(self, obj):
        if not hasattr(obj, "ticket"):
            return ""
        return obj.ticket.status

    def get_checked_in_at(self, obj):
        if not hasattr(obj, "ticket"):
            return None
        return obj.ticket.checked_in_at

    def get_participation_verified(self, obj):
        return hasattr(obj, "participation_record")


class EventRejectionSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=2000, trim_whitespace=True)


class EventSerializer(serializers.ModelSerializer):
    location = EventLocationSerializer()
    source = EventSourceSerializer()
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ("organizer", "moderation_status", "created_at", "updated_at")

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        deadline = attrs.get("deadline", getattr(self.instance, "deadline", None))
        price_type = attrs.get("price_type", getattr(self.instance, "price_type", None))
        price_amount = attrs.get("price_amount", getattr(self.instance, "price_amount", None))
        currency = attrs.get("currency", getattr(self.instance, "currency", ""))
        event_format = attrs.get("format", getattr(self.instance, "format", None))
        is_online = attrs.get(
            "is_online",
            event_format in {Event.Format.ONLINE, Event.Format.HYBRID},
        )
        online_url = attrs.get("online_url", getattr(self.instance, "online_url", ""))

        if ends_at and starts_at and ends_at < starts_at:
            raise serializers.ValidationError({"ends_at": "End time cannot precede start time."})
        if deadline and starts_at and deadline > starts_at:
            raise serializers.ValidationError({"deadline": "Deadline cannot be after the event starts."})
        if price_type == Event.PriceType.PAID and price_amount is None:
            raise serializers.ValidationError({"price_amount": "Paid events require a price amount."})
        if price_amount is not None and price_amount < 0:
            raise serializers.ValidationError({"price_amount": "Price cannot be negative."})
        if price_amount is not None and not currency:
            raise serializers.ValidationError({"currency": "Priced events require a currency."})
        if currency and len(currency) != 3:
            raise serializers.ValidationError({"currency": "Use a three-letter currency code."})
        if is_online and not online_url:
            raise serializers.ValidationError({"online_url": "Online events require an online URL."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        location_data = validated_data.pop("location")
        source_data = validated_data.pop("source")
        user = self.context["request"].user
        if "is_online" not in validated_data:
            validated_data["is_online"] = validated_data.get("format") in {
                Event.Format.ONLINE,
                Event.Format.HYBRID,
            }
        if "price_type" not in validated_data:
            validated_data["price_type"] = (
                Event.PriceType.FREE
                if validated_data.get("is_free", True)
                else Event.PriceType.UNKNOWN
            )
        event = Event.objects.create(
            organizer=user,
            moderation_status=Event.Status.PENDING_REVIEW,
            **validated_data,
        )
        EventLocation.objects.create(event=event, **location_data)
        EventSource.objects.create(event=event, **source_data)
        EventSubmission.objects.create(event=event, submitted_by=user)
        return event

    @transaction.atomic
    def update(self, instance, validated_data):
        location_data = validated_data.pop("location", None)
        source_data = validated_data.pop("source", None)
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()

        if location_data is not None:
            EventLocation.objects.update_or_create(event=instance, defaults=location_data)
        if source_data is not None:
            EventSource.objects.update_or_create(event=instance, defaults=source_data)
        return instance


class OrganizerModerationSerializer(serializers.Serializer):
    """One organizer account plus their current moderation standing."""

    id = serializers.IntegerField(source="pk", read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    event_count = serializers.IntegerField(read_only=True)
    moderation_status = serializers.SerializerMethodField()
    moderation_reason = serializers.SerializerMethodField()
    reviewed_at = serializers.SerializerMethodField()

    def get_moderation_status(self, user) -> str:
        record = getattr(user, "organizer_moderation", None)
        return record.status if record else OrganizerModeration.Status.PENDING

    def get_moderation_reason(self, user) -> str:
        record = getattr(user, "organizer_moderation", None)
        return record.reason if record else ""

    def get_reviewed_at(self, user):
        record = getattr(user, "organizer_moderation", None)
        return record.reviewed_at if record else None


class OrganizerModerationActionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrganizerModeration.Status.choices)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class OrganizerApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerApplication
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "telegram_username",
            "description",
            "project_link",
            "motivation",
            "experience",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def validate_telegram_username(self, value: str) -> str:
        cleaned = value.strip().lstrip("@")
        if not cleaned:
            raise serializers.ValidationError("Telegram username is required.")
        return cleaned

    def validate_first_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("First name is required.")
        return value.strip()

    def validate_last_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Last name is required.")
        return value.strip()

    def validate_description(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Description is required.")
        return value.strip()

    def validate_motivation(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("This field is required.")
        return value.strip()

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        # One live request at a time: a pending application already covers
        # the intent, so a second submission before it's decided would just
        # create noise for whoever reviews these.
        if user is not None and OrganizerApplication.objects.filter(
            applicant=user, status=OrganizerApplication.Status.PENDING
        ).exists():
            raise serializers.ValidationError(
                "You already have a pending organizer application."
            )
        return attrs


class OrganizerApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerApplication
        fields = ("id", "status", "created_at", "reviewed_at")
        read_only_fields = fields

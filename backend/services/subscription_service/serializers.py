from rest_framework import serializers

from .models import BillingRecord, Plan, Subscription, SubscriptionCancellation, UsageLimit


class UsageLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageLimit
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    limits = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "plan",
            "period_started_at",
            "ai_message_count",
            "essay_review_count",
            "saved_events_count",
            "limits",
        )

    def get_limits(self, obj):
        limit = UsageLimit.objects.filter(plan=obj.plan).first()
        return UsageLimitSerializer(limit).data if limit else None


class CheckoutSessionRequestSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=[Plan.STARTER, Plan.GROWTH, Plan.PREMIUM])


class BillingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingRecord
        fields = ("id", "provider", "amount", "currency", "status", "plan", "created_at")


class SubscriptionCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionCancellation
        fields = ("id", "requested_at", "effective_at", "reason")


class CancellationRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, allow_blank=True, required=False, default="")


class WebhookEventSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=30)
    event_id = serializers.CharField(max_length=120)
    event_type = serializers.CharField(max_length=60)
    payload = serializers.DictField(required=False, default=dict)


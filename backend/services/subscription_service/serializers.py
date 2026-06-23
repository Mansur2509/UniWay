from rest_framework import serializers

from .models import Subscription, UsageLimit


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


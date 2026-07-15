import json

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.throttling import ScopedIPRateThrottle

from .billing import (
    create_sandbox_checkout_session,
    log_billing_action,
    process_webhook_event,
    request_cancellation,
    verify_webhook_signature,
)
from .models import BillingRecord, Plan, Subscription
from .serializers import (
    BillingRecordSerializer,
    CancellationRequestSerializer,
    CheckoutSessionRequestSerializer,
    SubscriptionCancellationSerializer,
    SubscriptionSerializer,
    WebhookEventSerializer,
)
from .services import reset_usage_if_period_elapsed


class SubscriptionViewSet(viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        subscription = Subscription.objects.filter(user=request.user).first() or Subscription(
            user=request.user,
            plan=Plan.FREE,
        )
        subscription = reset_usage_if_period_elapsed(subscription, persist=False)
        return Response(self.get_serializer(subscription).data)


class BillingCheckoutSessionView(APIView):
    """Creates a sandbox checkout session only -- no real provider is ever
    contacted, no card data is ever received, and the returned URL never
    resolves to a live payment page (see billing.create_sandbox_checkout_session)."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle, ScopedIPRateThrottle]
    throttle_scope = "billing_checkout"

    def post(self, request):
        serializer = CheckoutSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data["plan"]

        result = create_sandbox_checkout_session(user=request.user, plan=plan)
        log_billing_action(
            actor=request.user,
            action="checkout_session_created",
            target_user=request.user,
            metadata={"plan": plan, "billing_record_id": result["billing_record_id"]},
        )
        return Response(result, status=status.HTTP_201_CREATED)


class BillingWebhookView(APIView):
    """Receives sandbox billing-provider webhooks. Public by necessity (the
    provider is the caller, not an authenticated UniWay user) -- authenticity
    is established entirely by the HMAC signature header over the raw body,
    never by payload content alone. An unsigned or badly-signed payload is
    rejected before anything ever reaches WebhookEvent."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle, ScopedIPRateThrottle]
    throttle_scope = "billing_webhook"

    def post(self, request):
        signature = request.META.get("HTTP_X_BILLING_SIGNATURE", "")
        if not verify_webhook_signature(payload_body=request.body, provided_signature=signature):
            return Response(
                {"detail": "Invalid or missing webhook signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            body = json.loads(request.body or b"{}")
        except ValueError:
            return Response({"detail": "Malformed JSON body."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WebhookEventSerializer(data=body)
        serializer.is_valid(raise_exception=True)
        result = process_webhook_event(**serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)


class BillingCancelView(APIView):
    """Requests cancellation at the end of the current paid period -- never
    an immediate downgrade (see billing.request_cancellation)."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle, ScopedIPRateThrottle]
    throttle_scope = "billing_cancel"

    def post(self, request):
        subscription = Subscription.objects.filter(user=request.user).first()
        if subscription is None or subscription.plan == Plan.FREE:
            return Response(
                {"detail": "There is no active paid subscription to cancel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CancellationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cancellation = request_cancellation(
            subscription=subscription, reason=serializer.validated_data["reason"]
        )
        log_billing_action(
            actor=request.user,
            action="cancellation_requested",
            target_user=request.user,
            metadata={"effective_at": cancellation.effective_at.isoformat()},
        )
        return Response(
            SubscriptionCancellationSerializer(cancellation).data, status=status.HTTP_201_CREATED
        )


class BillingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = BillingRecord.objects.filter(user=request.user)
        return Response(BillingRecordSerializer(records, many=True).data)

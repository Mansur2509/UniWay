from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Plan, Subscription
from .serializers import SubscriptionSerializer
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

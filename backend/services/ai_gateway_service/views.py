from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .serializers import MentorRequestSerializer


class MentorPlaceholderView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai"

    def post(self, request):
        serializer = MentorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "code": "ai_gateway_not_configured",
                "detail": "AI provider access is intentionally deferred to task AI-001.",
                "disclaimer": (
                    "AI guidance is informational. Verify important admissions, event, finance, "
                    "and academic information with official sources."
                ),
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


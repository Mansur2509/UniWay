from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.permissions import IsAdminRole

from .serializers import AIProfileAssessmentSerializer
from .services import DISCLAIMER, latest_assessment_envelope, run_profile_assessment

User = get_user_model()


def _serialize_envelope(result):
    return {
        "assessment": AIProfileAssessmentSerializer(result.assessment).data
        if result.assessment
        else None,
        "cached": result.cached,
        "reason": result.reason,
        "can_refresh": result.can_refresh,
        "next_available_at": result.next_available_at,
        "ai_available": result.ai_available,
        "disclaimer": DISCLAIMER,
    }


class LatestProfileAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_serialize_envelope(latest_assessment_envelope(request.user)))


class RunProfileAssessmentView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai"

    def post(self, request):
        return Response(_serialize_envelope(run_profile_assessment(request.user)))


class AdminRunProfileAssessmentView(APIView):
    permission_classes = [IsAdminRole]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai"

    def post(self, request, user_id: int):
        target_user = get_object_or_404(User, pk=user_id)
        return Response(
            _serialize_envelope(run_profile_assessment(target_user, force=True))
        )

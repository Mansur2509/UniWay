from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole

from .models import Institution, InstitutionMembership
from .serializers import (
    ConsentUpdateSerializer,
    InstitutionMembershipSerializer,
    InstitutionSerializer,
    InviteMemberSerializer,
    StudentSummaryRowSerializer,
)
from .services import (
    InstitutionAccessError,
    accept_invitation,
    institution_analytics,
    invite_member,
    student_summary_rows,
)

User = get_user_model()


class InstitutionCreateView(APIView):
    """Platform-admin-only for this foundation: real self-serve institution
    signup (with its own onboarding/verification flow) is out of scope
    here -- see docs/POST_V1_PRODUCT_ROADMAP_021.md Module C."""

    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = InstitutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        institution = serializer.save()

        manager_email = request.data.get("manager_email", "")
        manager = User.objects.filter(email__iexact=manager_email).first()
        if manager is None:
            return Response(
                {"manager_email": "No UniWay account exists for that email yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        InstitutionMembership.objects.create(
            institution=institution,
            user=manager,
            role=InstitutionMembership.MemberRole.SCHOOL_MANAGER,
            status=InstitutionMembership.Status.ACTIVE,
        )
        return Response(InstitutionSerializer(institution).data, status=status.HTTP_201_CREATED)


def _get_institution(slug: str) -> Institution:
    return get_object_or_404(Institution, slug=slug, is_active=True)


class InstitutionInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        institution = _get_institution(slug)
        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership = invite_member(
                institution=institution,
                inviter=request.user,
                email=serializer.validated_data["email"],
                role=serializer.validated_data["role"],
            )
        except InstitutionAccessError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            InstitutionMembershipSerializer(membership).data, status=status.HTTP_201_CREATED
        )


class MyMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        institution = _get_institution(slug)
        membership = InstitutionMembership.objects.filter(
            institution=institution, user=request.user
        ).first()
        if membership is None:
            return Response({"detail": "Not a member of this institution."}, status=status.HTTP_404_NOT_FOUND)
        return Response(InstitutionMembershipSerializer(membership).data)

    def patch(self, request, slug):
        """A student updates their own sharing consent -- never settable by
        anyone else, including a counselor or manager."""
        institution = _get_institution(slug)
        membership = get_object_or_404(InstitutionMembership, institution=institution, user=request.user)
        serializer = ConsentUpdateSerializer(membership, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(InstitutionMembershipSerializer(membership).data)


class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        institution = _get_institution(slug)
        membership = get_object_or_404(InstitutionMembership, institution=institution, user=request.user)
        try:
            accept_invitation(membership=membership, user=request.user)
        except (InstitutionAccessError, ValueError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InstitutionMembershipSerializer(membership).data)


class InstitutionStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        institution = _get_institution(slug)
        try:
            rows = student_summary_rows(institution=institution, viewer=request.user)
        except InstitutionAccessError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response({"results": StudentSummaryRowSerializer(rows, many=True).data})


class InstitutionAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        institution = _get_institution(slug)
        try:
            data = institution_analytics(institution=institution, viewer=request.user)
        except InstitutionAccessError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(data)

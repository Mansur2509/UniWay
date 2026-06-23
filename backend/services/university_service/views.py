from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from common.permissions import IsAdminOrReadOnly

from .models import University
from .serializers import UniversitySerializer


class UniversityViewSet(ModelViewSet):
    serializer_class = UniversitySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("name", "city", "country", "programs__name")
    filterset_fields = ("country",)
    ordering_fields = ("name", "country", "created_at")

    def get_queryset(self):
        queryset = University.objects.prefetch_related(
            "programs",
            "requirements",
            "scholarships",
            "data_sources",
        )
        user = self.request.user
        if user.is_authenticated and user.is_admin_role:
            return queryset
        return queryset.filter(is_published=True)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticated()]
        return super().get_permissions()

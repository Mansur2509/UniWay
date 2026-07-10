from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role)


class IsOrganizerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_organizer or request.user.is_admin_role)
        ):
            return False
        if request.user.is_admin_role:
            return True

        # Deferred import: common/ stays decoupled from specific services at
        # module-load time. Existing organizers with no moderation record
        # are unaffected -- only an explicit suspended/rejected row blocks.
        from services.event_service.models import OrganizerModeration

        return not OrganizerModeration.objects.filter(
            organizer=request.user,
            status__in=(OrganizerModeration.Status.SUSPENDED, OrganizerModeration.Status.REJECTED),
        ).exists()


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_role
        )


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner_id = (
            getattr(obj, "user_id", None)
            or getattr(obj, "owner_id", None)
            or getattr(obj, "organizer_id", None)
        )
        return bool(request.user.is_admin_role or owner_id == request.user.id)

from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Gates the /api/admin/ dashboard API — staff only, no anonymous or regular-user access."""

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

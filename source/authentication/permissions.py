from rest_framework import permissions


class IsOwnProfile(permissions.BasePermission):
    """Restrict users from accessing other profiles."""

    def has_permission(self, request, view):
        """Check if superuser or admin. Only superusers and admin can create new accounts."""
        if view.action in ["update", "retrieve"]:
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        """Check user is trying to access other profiles."""
        return obj.id == request.user.id


class IsSuperuser(permissions.BasePermission):
    """Allow only super user."""

    message = "Not superuser."

    def has_permission(self, request, view):
        return request.user.is_superuser


class IsInternalAdmin(permissions.BasePermission):
    """Allows only internal admin."""

    message = "Not an admin."

    def has_permission(self, request, view):
        return request.user.is_internal and (
            request.user.is_superuser or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

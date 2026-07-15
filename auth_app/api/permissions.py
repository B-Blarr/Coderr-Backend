"""Custom permission classes for the auth app."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Allow read to anyone; writes only to the profile's owner."""

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or when editing own profile."""
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user

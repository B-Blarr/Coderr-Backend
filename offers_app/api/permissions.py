"""Custom permission classes for the offers app."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Allow read to anyone; writes only to the offer's owner."""

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or when the user owns it."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsBusiness(BasePermission):
    """Allow access only to authenticated business users."""

    def has_permission(self, request, view):
        """Return True for authenticated business users."""
        return (request.user.is_authenticated
                and request.user.type == 'business')

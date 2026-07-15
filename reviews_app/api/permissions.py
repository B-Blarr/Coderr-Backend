"""Custom permission classes for the reviews app."""

from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Allow only authenticated users of type 'customer'."""

    def has_permission(self, request, view):
        """Return True for authenticated customer users."""
        return (request.user.is_authenticated
                and request.user.type == 'customer')


class IsOwner(BasePermission):
    """Allow object access only to the review's creator."""

    def has_object_permission(self, request, view, obj):
        """Return True only if the requester wrote the review."""
        return obj.reviewer == request.user

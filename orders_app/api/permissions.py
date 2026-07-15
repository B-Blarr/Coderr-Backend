"""Custom permission classes for the orders app."""

from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Allow only authenticated users of type 'customer'."""

    def has_permission(self, request, view):
        """Return True for authenticated customer users."""
        return (request.user.is_authenticated
                and request.user.type == 'customer')


class IsBusinessOwnerOfOrder(BasePermission):
    """Allow status updates only to the order's business user."""

    def has_object_permission(self, request, view, obj):
        """Return True only if the requester is the order's business."""
        return obj.business_user == request.user

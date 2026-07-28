"""API views for the reviews app."""

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review

from .permissions import IsCustomer, IsOwner
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """CRUD for reviews with filtering, ordering and role-based access."""

    queryset = Review.objects.all()

    def get_serializer_class(self):
        """Use the update serializer for PATCH/PUT, else the default."""
        if self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        """Attach the logged-in user as the review's reviewer."""
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        """Return reviews, optionally filtered/ordered by query params."""
        queryset = Review.objects.all()
        queryset = self._filter_by_id(
            queryset, 'business_user_id', 'business_user_id')
        queryset = self._filter_by_id(queryset, 'reviewer_id', 'reviewer_id')
        ordering = self.request.query_params.get('ordering')
        if ordering in ['updated_at', '-updated_at', 'rating', '-rating']:
            queryset = queryset.order_by(ordering)
        return queryset

    def _filter_by_id(self, queryset, param, field):
        """Filter by a numeric id, ignoring the parameter when empty.

        The frontend always sends every filter, including the empty ones.
        An empty value therefore means "no filter" and must not be treated
        as an invalid number.
        """
        raw = self.request.query_params.get(param, '').strip()
        if not raw:
            return queryset
        try:
            value = int(raw)
        except (TypeError, ValueError):
            raise ValidationError({param: 'Must be a number.'})
        return queryset.filter(**{field: value})

    def get_permissions(self):
        """Map each action to its required permission class."""
        if self.action == 'create':
            return [IsCustomer()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwner()]
        return [IsAuthenticated()]

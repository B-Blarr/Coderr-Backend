"""API views for the reviews app."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from reviews_app.models import Review
from .permissions import IsCustomer, IsOwner


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

        business_user_id = self.request.query_params.get('business_user_id')
        if business_user_id is not None:
            queryset = queryset.filter(business_user_id=business_user_id)
        reviewer_id = self.request.query_params.get('reviewer_id')
        if reviewer_id is not None:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        ordering = self.request.query_params.get('ordering')
        if ordering in ['updated_at', '-updated_at', 'rating', '-rating']:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_permissions(self):
        """Map each action to its required permission class."""
        if self.action == 'create':
            return [IsCustomer()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwner()]
        return [IsAuthenticated()]

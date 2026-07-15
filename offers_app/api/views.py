"""API views for the offers app."""

from django.db.models import Q, Min
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from offers_app.models import Offer, OfferDetail
from .serializers import OfferCreateSerializer, OfferSerializer, \
    OfferDetailSerializer
from .permissions import IsOwnerOrReadOnly, IsBusiness
from .pagination import OfferPagination


class OfferViewSet(viewsets.ModelViewSet):
    """CRUD for offers with filtering, search, ordering and pagination."""

    queryset = Offer.objects.all()
    pagination_class = OfferPagination

    def get_serializer_class(self):
        """Use the create serializer for writes, else the read one."""
        if self.action in ['create', 'update', 'partial_update']:
            return OfferCreateSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        """Attach the logged-in user as the offer's owner."""
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """Map each action to its required permission class."""
        if self.action == 'create':
            return [IsBusiness()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        """Annotate min price/delivery, then filter and order."""
        queryset = Offer.objects.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
        )
        queryset = self._filter_search(queryset)
        queryset = self._filter_creator(queryset)
        queryset = self._filter_min_price(queryset)
        queryset = self._filter_max_delivery(queryset)
        return self._apply_ordering(queryset)

    def _filter_search(self, queryset):
        """Filter by a search term in title or description."""
        search = self.request.query_params.get('search')
        if search is not None:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search))
        return queryset

    def _filter_creator(self, queryset):
        """Filter offers by their creator's user id."""
        creator_id = self.request.query_params.get('creator_id')
        if creator_id is not None:
            queryset = queryset.filter(user_id=creator_id)
        return queryset

    def _filter_min_price(self, queryset):
        """Filter offers by a minimum price."""
        min_price = self.request.query_params.get('min_price')
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)
        return queryset

    def _filter_max_delivery(self, queryset):
        """Filter offers by a maximum delivery time."""
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time is not None:
            queryset = queryset.filter(
                min_delivery_time__lte=max_delivery_time)
        return queryset

    def _apply_ordering(self, queryset):
        """Order by an allowed field, defaulting to newest first."""
        ordering = self.request.query_params.get('ordering')
        allowed = ['updated_at', '-updated_at', 'min_price', '-min_price']
        if ordering in allowed:
            return queryset.order_by(ordering)
        return queryset.order_by('-updated_at')


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Retrieve a single offer detail by id."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer

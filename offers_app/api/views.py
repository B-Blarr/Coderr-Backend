from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from offers_app.models import Offer
from .serializers import OfferCreateSerializer, OfferSerializer
from .permissions import IsOwnerOrReadOnly, IsBusiness


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OfferCreateSerializer
        return OfferSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsBusiness()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return [AllowAny()]
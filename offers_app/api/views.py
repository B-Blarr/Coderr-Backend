from rest_framework import viewsets
from offers_app.models import Offer
from .serializers import OfferCreateSerializer, OfferSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OfferCreateSerializer
        return OfferSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
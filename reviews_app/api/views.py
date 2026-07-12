from rest_framework import viewsets
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from reviews_app.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
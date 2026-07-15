"""API view for the aggregated platform statistics (base-info)."""

from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    """Return platform-wide counts and the average rating."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return review/offer/profile counts and the average rating."""
        average = Review.objects.aggregate(Avg('rating'))['rating__avg']
        return Response({
            'review_count': Review.objects.count(),
            'average_rating': round(average, 1) if average is not None else 0,
            'business_profile_count': User.objects.filter(
                type='business').count(),
            'offer_count': Offer.objects.count(),
        })

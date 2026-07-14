from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from reviews_app.models import Review
from offers_app.models import Offer
from auth_app.models import User


class BaseInfoView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        average = Review.objects.aggregate(Avg('rating'))['rating__avg']
        return Response({
            'review_count': Review.objects.count(),
            'average_rating': round(average, 1) if average is not None else 0,
            'business_profile_count': User.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count(),
        })
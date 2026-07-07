from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailRetrieveView

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = router.urls + [
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]



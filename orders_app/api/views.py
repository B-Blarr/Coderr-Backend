from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import OrderSerializer, OrderUpdateSerializer
from orders_app.models import Order
from auth_app.models import User
from .permissions import IsCustomer, IsBusinessOwnerOfOrder


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(customer_user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user))

    def get_permissions(self):
        if self.action == 'create':
            return [IsCustomer()]
        if self.action in ['update', 'partial_update']:
            return [IsBusinessOwnerOfOrder()]
        if self.action in ['destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class OrderCountView(APIView):

    def get(self, request, business_user_id):
        get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    def get(self, request, business_user_id):
        get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count})

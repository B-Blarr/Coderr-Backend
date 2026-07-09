from django.db.models import Q
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import OrderSerializer, OrderUpdateSerializer
from orders_app.models import Order
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
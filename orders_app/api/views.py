from django.db.models import Q
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer
from orders_app.models import Order
from .permissions import IsCustomer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        # if self.action in ['create', 'update', 'partial_update']:
        #     return OrderCreateSerializer
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
        return [IsAuthenticated()]
"""API views for the orders app."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User
from orders_app.models import Order

from .permissions import IsBusinessOwnerOfOrder, IsCustomer
from .serializers import OrderSerializer, OrderUpdateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD for orders with role-based access and own-orders filter."""

    queryset = Order.objects.all()

    def get_serializer_class(self):
        """Use the update serializer for PATCH/PUT, else the default."""
        if self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        """Attach the logged-in user as the order's customer."""
        serializer.save(customer_user=self.request.user)

    def get_queryset(self):
        """Return all orders for staff, else only the user's own."""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user))

    def get_permissions(self):
        """Map each action to its required permission class."""
        if self.action == 'create':
            return [IsCustomer()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsBusinessOwnerOfOrder()]
        if self.action in ['destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class OrderCountView(APIView):
    """Return the count of a business's in-progress orders."""

    def get(self, request, business_user_id):
        """Return the in-progress order count for the business user."""
        get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """Return the count of a business's completed orders."""

    def get(self, request, business_user_id):
        """Return the completed order count for the business user."""
        get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count})

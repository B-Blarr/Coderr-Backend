"""Serializers for the orders app API."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """Read/create serializer; builds an order from an offer detail."""

    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type',
                  'status', 'created_at', 'updated_at', 'offer_detail_id']

        read_only_fields = ['customer_user', 'business_user', 'title',
                            'revisions', 'delivery_time_in_days', 'price',
                            'features', 'offer_type', 'status']

    def create(self, validated_data):
        """Create an order by snapshotting the chosen offer detail."""
        offer_detail_id = validated_data.pop('offer_detail_id')
        detail = get_object_or_404(OfferDetail, id=offer_detail_id)
        return Order.objects.create(
            customer_user=validated_data['customer_user'],
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type
        )


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Update serializer; only the status field is editable."""

    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type',
                  'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer_user', 'business_user', 'title',
                            'revisions', 'delivery_time_in_days', 'price',
                            'features', 'offer_type', 'created_at',
                            'updated_at']

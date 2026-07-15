"""Serializers for the offers app API."""

from rest_framework import serializers

from auth_app.models import User
from offers_app.models import Offer, OfferDetail


class UserDetailsSerializer(serializers.ModelSerializer):
    """Minimal creator info embedded in offer responses."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Expose an offer detail as an id plus its URL."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Return the relative URL of the offer detail."""
        return f'/offerdetails/{obj.id}/'


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full representation of a single offer detail (tier)."""

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']


class OfferSerializer(serializers.ModelSerializer):
    """Read serializer for offers with computed price/delivery fields."""

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = UserDetailsSerializer(source='user', read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time',
                  'user_details']

        read_only_fields = ['user']

    def get_min_price(self, obj):
        """Return the lowest price among the offer's details."""
        prices = [detail.price for detail in obj.details.all()]
        return min(prices)

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time among the details."""
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times)


class OfferCreateSerializer(serializers.ModelSerializer):
    """Create/update serializer that manages the three tiers."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'details']

        read_only_fields = ['user']

    def create(self, validated_data):
        """Create the offer and its nested detail tiers."""
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def validate_details(self, value):
        """Validate the detail tiers for create and update."""
        if self.instance is None:
            return self._validate_create_details(value)
        return self._validate_update_details(value)

    def _validate_create_details(self, value):
        """On create, require exactly one detail per offer_type."""
        if len(value) != 3:
            raise serializers.ValidationError(
                'Exactly 3 Details are needed.')
        types = [detail['offer_type'] for detail in value]
        if set(types) != {'basic', 'standard', 'premium'}:
            raise serializers.ValidationError(
                'Exactly one basic, standard and premium '
                'detail are needed.')
        return value
    
    def _validate_update_details(self, value):
        """On update, each detail must match an existing offer_type."""
        existing = set(
            self.instance.details.values_list('offer_type', flat=True))
        for detail in value:
            if detail.get('offer_type') not in existing:
                raise serializers.ValidationError(
                    'Each detail needs a valid offer_type of this offer.')
        return value

    def update(self, instance, validated_data):
        """Update the offer and its details, matched by offer type."""
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if details_data is not None:
            for detail in details_data:
                detail_obj = instance.details.get(
                    offer_type=detail['offer_type'])
                for attr, value in detail.items():
                    setattr(detail_obj, attr, value)
                detail_obj.save()
        return instance
from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from auth_app.models import User


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferDetailLinkSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f'/offerdetails/{obj.id}/'
    

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model =OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']


class OfferSerializer(serializers.ModelSerializer):

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
        prices = [detail.price for detail in obj.details.all()]
        return min(prices)
    
    def get_min_delivery_time(self, obj):
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times)


class OfferCreateSerializer(serializers.ModelSerializer):
        
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'details']
        
        read_only_fields = ['user']

    def create(self, validated_data):
        details_data = validated_data.pop('details')   
        offer = Offer.objects.create(**validated_data)   
        for detail in details_data:                      
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def validate_details(self, value):
        if self.instance is None:
            if len(value) != 3:
                raise serializers.ValidationError('Exactly 3 Details are needed.')
            types = [detail['offer_type'] for detail in value]
            if set(types) != {'basic', 'standard', 'premium'}:
                raise serializers.ValidationError(
                    'Exactly one basic, standard and premium detail are needed.')
        return value

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if details_data is not None:
            for detail in details_data:
                detail_obj = instance.details.get(offer_type=detail['offer_type'])
                for attr, value in detail.items():
                    setattr(detail_obj, attr, value)
                detail_obj.save()
        return instance
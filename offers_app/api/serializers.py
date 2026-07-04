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

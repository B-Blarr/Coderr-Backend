from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description',
                  'created_at', 'updated_at']
        
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate(self, attrs):
        reviewer = self.context['request'].user
        business_user = attrs['business_user']
        already_reviewed = Review.objects.filter(
            business_user=business_user, reviewer=reviewer).exists()
        if already_reviewed:
            raise serializers.ValidationError(
                'You already gave a review to this business user.')
        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description',
                  'created_at', 'updated_at']
        read_only_fields = ['business_user', 'reviewer',
                  'created_at', 'updated_at']
from rest_framework import serializers
from django.contrib.auth import authenticate
from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
        
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, attrs):

        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):                
        validated_data.pop('repeated_password')
        return User.objects.create_user(**validated_data)
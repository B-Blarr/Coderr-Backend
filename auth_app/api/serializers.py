"""Serializers for the auth app API."""

from rest_framework import serializers
from django.contrib.auth import authenticate
from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create a new user from registration data."""

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
        """Ensure the two password fields match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        """Create the user, dropping the confirmation password."""
        validated_data.pop('repeated_password')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Authenticate a user from username and password."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate the credentials and attach the user."""
        user = authenticate(
            username=data['username'],
            password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        data['user'] = user
        return data


class ProfileDetailSerializer(serializers.ModelSerializer):
    """Full profile representation for detail and update."""

    user = serializers.IntegerField(read_only=True, source='id')

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email',
            'created_at'
        ]
        read_only_fields = ['username', 'type', 'created_at']


class BusinessProfileSerializer(serializers.ModelSerializer):
    """Business-user profile fields for the business list."""

    user = serializers.IntegerField(read_only=True, source='id')

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type'
        ]
        read_only_fields = ['username', 'type']


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Customer-user profile fields for the customer list."""

    user = serializers.IntegerField(read_only=True, source='id')
    uploaded_at = serializers.DateTimeField(
        read_only=True, source='created_at')

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type'
        ]
        read_only_fields = ['username', 'type']

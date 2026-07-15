"""API views for the auth app: registration, login and profiles."""

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User

from .permissions import IsOwnerOrReadOnly
from .serializers import (BusinessProfileSerializer, CustomerProfileSerializer,
                          LoginSerializer, ProfileDetailSerializer,
                          RegistrationSerializer)


class RegistrationView(APIView):
    """Register a new user and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create the user and return token and account data."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(APIView):
    """Authenticate a user and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate credentials and return token and account data."""
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a single user profile (owner may edit)."""

    queryset = User.objects.all()
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class BusinessProfileView(generics.ListAPIView):
    """List all business-type user profiles."""

    queryset = User.objects.filter(type='business')
    serializer_class = BusinessProfileSerializer


class CustomerProfileView(generics.ListAPIView):
    """List all customer-type user profiles."""

    queryset = User.objects.filter(type='customer')
    serializer_class = CustomerProfileSerializer

"""Tests for the auth app endpoints."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    """Test registration, login, profile and profile lists."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='loginuser', password='pass1234', type='customer')

    def test_registration(self):
        url = reverse('registration')
        data = {
            'username': 'newuser', 'email': 'new@test.de',
            'password': 'pass1234', 'repeated_password': 'pass1234',
            'type': 'customer',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_password_mismatch_returns_400(self):
        url = reverse('registration')
        data = {
            'username': 'newuser', 'email': 'new@test.de',
            'password': 'pass1234', 'repeated_password': 'differentpassword',
            'type': 'customer',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('repeated_password', response.data)

    def test_login(self):
        url = reverse('login')
        data = {'username': 'loginuser', 'password': 'pass1234'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        expected_fields = {
            'token', 'username', 'email', 'user_id'
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_login_wrong_password_returns_400(self):
        url = reverse('login')
        data = {'username': 'loginuser', 'password': 'wrong_password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileTests(APITestCase):
    """Test profile detail/update and the business/customer lists."""

    def setUp(self):
        self.business = User.objects.create_user(
            username='testuserB', password='testpassword', type='business')
        self.customer = User.objects.create_user(
            username='testuserC', password='testpassword', type='customer')

    def test_get_profile_detail(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('profile-detail', kwargs={'pk': self.business.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = {
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email',
            'created_at',
        }
        self.assertEqual(set(response.data.keys()), expected_fields)
        self.assertEqual(response.data['user'], self.business.id)
        self.assertEqual(response.data['type'], 'business')
        self.assertEqual(response.data['location'], '')

    def test_get_profile_unknown_pk_returns_404(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('profile-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile_detail(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('profile-detail', kwargs={'pk': self.business.id})
        data = {'first_name': 'Max', 'location': 'Berlin'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')
        self.assertEqual(response.data['location'], 'Berlin')
        self.business.refresh_from_db()
        self.assertEqual(self.business.first_name, 'Max')
        self.assertEqual(self.business.location, 'Berlin')

    def test_patch_profile_unauthenticated_returns_401(self):
        url = reverse('profile-detail', kwargs={'pk': self.business.id})
        response = self.client.patch(url, {'first_name': 'Max'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_foreign_profile_returns_403(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('profile-detail', kwargs={'pk': self.business.id})
        response = self.client.patch(
            url, {'first_name': 'Hack'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_business_list(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('business-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        expected = {'user', 'username', 'first_name', 'last_name', 'file',
                    'location', 'tel', 'description', 'working_hours', 'type'}
        self.assertEqual(set(response.data[0].keys()), expected)

    def test_customer_list(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('customer-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        expected = {'user', 'username', 'first_name', 'last_name', 'file',
                    'uploaded_at', 'type'}
        self.assertEqual(set(response.data[0].keys()), expected)

    def test_model_str_representation(self):
        self.assertEqual(str(self.business), 'testuserB')

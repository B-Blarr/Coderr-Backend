"""Tests for the reviews app endpoints."""

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from reviews_app.models import Review

User = get_user_model()


class ReviewsTests(APITestCase):
    """Test review CRUD, filtering and permissions."""

    def setUp(self):
        self.business = User.objects.create_user(
            username='business', password='pass1234', type='business')
        self.other_business = User.objects.create_user(
            username='other_business', password='pass1234', type='business')
        self.customer = User.objects.create_user(
            username='customer', password='pass1234', type='customer')
        self.other_customer = User.objects.create_user(
            username='other_customer', password='pass1234', type='customer')

        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=4, description='Nice Work.')

    def test_get_reviews_list(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_reviews_list_not_authenticated_returns_401(self):
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_as_customer(self):
        self.client.force_authenticate(user=self.other_customer)
        url = reverse('review-list')
        data = {'business_user': self.business.id, 'rating': 5,
                'description': 'Great work!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.other_customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['rating'], 5)

    def test_create_review_as_business_returns_403(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('review-list')
        data = {'business_user': self.business.id, 'rating': 5,
                'description': 'Great work!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate_review_returns_400(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('review-list')
        data = {'business_user': self.business.id, 'rating': 3,
                'description': 'Again.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_review_as_owner(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('review-detail', kwargs={'pk': self.review.id})
        response = self.client.patch(url, {'rating': '4'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)

    def test_filter_reviews(self):
        Review.objects.create(
            business_user=self.other_business, reviewer=self.other_customer,
            rating=5, description='Other.')

        self.client.force_authenticate(user=self.customer)
        url = reverse('review-list')
        response = self.client.get(url, {
            'business_user_id': self.business.id,
            'reviewer_id': self.customer.id,
            'ordering': 'rating',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

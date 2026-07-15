"""Tests for the base-info endpoint."""

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from reviews_app.models import Review
from offers_app.models import Offer


User = get_user_model()


class BaseInfoTests(APITestCase):
    """Test the aggregated platform statistics."""

    def setUp(self):

        self.business = User.objects.create_user(
            username='business', password='pass1234', type='business')
        self.customer = User.objects.create_user(
            username='customer', password='pass1234', type='customer')
        self.another_customer = User.objects.create_user(
            username='another_customer', password='pass1234', type='customer')
        Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=4, description='Nice Work.')
        Review.objects.create(
            business_user=self.business, reviewer=self.another_customer,
            rating=2, description='Very Good.')
        self.offer = Offer.objects.create(
            user=self.business, title='Test Offer', description='description')

    def test_base_info(self):
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['average_rating'], 3.0)
        self.assertEqual(response.data['business_profile_count'], 1)
        self.assertEqual(response.data['offer_count'], 1)

    def test_base_info_no_reviews(self):
        Review.objects.all().delete()
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_rating'], 0)

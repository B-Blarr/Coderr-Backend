from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from reviews_app.models import Review

User = get_user_model()


class ReviewsTests(APITestCase):

    def setUp(self):
        self.business = User.objects.create_user(
            username='busi', password='pass1234', type='business')
        self.other_business = User.objects.create_user(
            username='busi2', password='pass1234', type='business')
        self.customer = User.objects.create_user(
            username='custo', password='pass1234', type='customer')
        self.other_customer = User.objects.create_user(
            username='custo2', password='pass1234', type='customer')

        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=4, description='Nice Work.')
        

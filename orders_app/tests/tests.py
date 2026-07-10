from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from orders_app.models import Order
from offers_app.models import Offer, OfferDetail

User = get_user_model()

class OrderTests(APITestCase):

    def setUp(self):

        self.business = User.objects.create_user(
            username='busi', password='pass1234', type='business')
        self.other_business = User.objects.create_user(
            username='busi2', password='pass1234', type='business')
        self.customer = User.objects.create_user(
            username='custo', password='pass1234', type='customer')
        self.admin = User.objects.create_user(
            username='admin', password='pass1234', type='customer', is_staff=True)
        
        self.offer = Offer.objects.create(
            user=self.business, title='Test Offer', description='description')
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=1, delivery_time_in_days=5,
            price='100.00', features=['feature'], offer_type='basic')

        self.order = Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            title='Basic', revisions=1, delivery_time_in_days=5, price='100.00',
            features=['feature'], offer_type='basic', status='in_progress')

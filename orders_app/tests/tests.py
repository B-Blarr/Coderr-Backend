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
            username='business', password='pass1234', type='business')
        self.other_business = User.objects.create_user(
            username='other_business', password='pass1234', type='business')
        self.customer = User.objects.create_user(
            username='customer', password='pass1234', type='customer')
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

    def test_get_order_list(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_order_list_not_authenticated(self):
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        response = self.client.post(
            url, {'offer_detail_id': self.detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['title'], 'Basic')

    def test_create_order_as_business_returns_403(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('order-list')
        response = self.client.post(
            url, {'offer_detail_id': self.detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_as_unauthorized_returns_401(self):
        url = reverse('order-list')
        response = self.client.post(
            url, {'offer_detail_id': self.detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_status_as_busines(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.patch(
            url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_patch_order_status_as_customer_returns_403(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.patch(
            url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_str_representation(self):
        self.assertEqual(str(self.order), 'Basic')

    def test_order_count(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse(
            'order-count', kwargs={'business_user_id': self.business.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('completed-order-count',
                      kwargs={'business_user_id': self.business.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 0)

    def test_delete_order_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

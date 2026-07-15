"""Tests for the offers app endpoints."""

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferTests(APITestCase):
    """Test offer CRUD, filtering and permissions."""

    def setUp(self):

        self.business = User.objects.create_user(
            username='busi', password='pass1234', type='business')
        self.other_business = User.objects.create_user(
            username='busi2', password='pass1234', type='business')
        self.customer = User.objects.create_user(
            username='custo', password='pass1234', type='customer')

        self.offer = Offer.objects.create(
            user=self.business, title='Test Offer', description='description')
        details = [('basic', 100, 5), ('standard', 200, 4),
                   ('premium', 300, 3)]
        for offer_type, price, days in details:
            OfferDetail.objects.create(
                offer=self.offer, title=offer_type.capitalize(), revisions=1,
                delivery_time_in_days=days, price=price,
                features=['feature'], offer_type=offer_type)

    def _offer_data(self):
        return {
            'title': 'Neues Offer',
            'description': 'Beschreibung',
            'details': [
                {'title': 'Basic', 'revisions': 1,
                 'delivery_time_in_days': 5, 'price': '100.00',
                 'features': ['Logo'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2,
                 'delivery_time_in_days': 4, 'price': '200.00',
                 'features': ['Logo', 'Karte'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3,
                 'delivery_time_in_days': 3, 'price': '300.00',
                 'features': ['Logo', 'Karte', 'Flyer'],
                 'offer_type': 'premium'},
            ],
        }

    def test_create_offer_as_business(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('offer-list')
        response = self.client.post(url, self._offer_data(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_offer = Offer.objects.get(title='Neues Offer')
        self.assertEqual(new_offer.details.count(), 3)
        self.assertEqual(new_offer.user, self.business)

    def test_create_offer_as_customer_returns_403(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('offer-list')
        response = self.client.post(url, self._offer_data(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_invalid_details_returns_400(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('offer-list')
        data = self._offer_data()
        data['details'].pop()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)

    def test_get_offer(self):
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_offer_detail(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)
        self.assertEqual(response.data['title'], 'Test Offer')

    def test_patch_offer(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.patch(url, {'title': 'Changed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Changed')

    def test_patch_offer_not_as_owner_returns_403(self):
        self.client.force_authenticate(user=self.other_business)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.patch(url, {'title': 'Changed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer(self):
        self.client.force_authenticate(user=self.business)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_offer_not_as_owner_returns_403(self):
        self.client.force_authenticate(user=self.other_business)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_filter_creator_id(self):
        url = reverse('offer-list')
        response = self.client.get(url, {'creator_id': self.business.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for offer in response.data['results']:
            self.assertEqual(offer['user'], self.business.id)

    def test_model_str_representation(self):
        self.assertEqual(str(self.offer), 'Test Offer')
        basic = self.offer.details.get(offer_type='basic')
        self.assertEqual(str(basic), 'Basic')

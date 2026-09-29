"""Tests for the contact app."""

from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from contact_app.models import ContactMessage


class ContactEndpointTests(APITestCase):
    """Guard the contact endpoint until its full tests exist.

    Throttles are set up before the view runs, so a missing throttle
    rate in the settings makes every request fail with 500.
    """

    def test_invalid_message_returns_400(self):
        response = self.client.post(reverse('contact'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(CONTACT_RECIPIENT='inbox@example.com')
    def test_valid_message_is_stored_and_sent(self):
        payload = {
            'name': 'Test Person',
            'email': 'test@example.com',
            'message': 'Eine Testnachricht mit genug Text.',
        }
        response = self.client.post(reverse('contact'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ContactMessage.objects.get().mail_sent)
        self.assertEqual(mail.outbox[0].reply_to, ['test@example.com'])

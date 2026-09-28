"""Tests for the contact app."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ContactEndpointTests(APITestCase):
    """Guard the contact endpoint until its full tests exist.

    Throttles are set up before the view runs, so a missing throttle
    rate in the settings makes every request fail with 500.
    """

    def test_invalid_message_returns_400(self):
        response = self.client.post(reverse('contact'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

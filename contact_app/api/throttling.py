"""Throttling classes for the contact app."""

from rest_framework.throttling import AnonRateThrottle

from core.throttling import RealIpMixin


class ContactRateThrottle(RealIpMixin, AnonRateThrottle):
    """Limits contact form submissions per client address."""

    scope = 'contact'

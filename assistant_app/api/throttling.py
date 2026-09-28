"""Throttling classes for the assistant app."""

from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle

from core.throttling import RealIpMixin


class AssistantRateThrottle(RealIpMixin, AnonRateThrottle):
    """Limits questions per client address."""

    scope = 'assistant'


class AssistantGlobalThrottle(SimpleRateThrottle):
    """Limits the questions of all clients together.

    Caps the daily cost even when many addresses take part. The price is
    that a busy day locks everybody out until the window moves on.
    """

    scope = 'assistant_global'

    def get_cache_key(self, request, view):
        """Return the same key for every client."""
        return self.cache_format % {'scope': self.scope, 'ident': 'all'}

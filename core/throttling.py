"""Throttling helpers shared by the apps that serve the portfolio."""


class RealIpMixin:
    """Identifies a client by the X-Real-IP header that Nginx sets.

    Django only ever sees the address of the local reverse proxy, so the
    real client address is taken from ``X-Real-IP``. Unlike
    ``X-Forwarded-For`` that header is overwritten by Nginx on every
    request and can therefore not be forged by the client.
    """

    def get_ident(self, request):
        """Return the client address, preferring Nginx' X-Real-IP."""
        real_ip = request.META.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip
        return super().get_ident(request)

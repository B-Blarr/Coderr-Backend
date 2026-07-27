"""API views for the contact app."""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ContactMessageSerializer
from .throttling import ContactRateThrottle

logger = logging.getLogger(__name__)


class ContactMessageView(APIView):
    """Accepts a contact form submission and forwards it by mail."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ContactRateThrottle]
    serializer_class = ContactMessageSerializer

    def post(self, request):
        """Store the message and send it to the configured recipient."""
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.pop('website', ''):
            logger.info("Kontaktformular: Honeypot ausgeloest, verworfen.")
            return Response(
                {'detail': 'Nachricht empfangen.'},
                status=status.HTTP_201_CREATED,
            )

        message = serializer.save(ip_address=self._client_ip(request))
        message.mail_sent = self._send_mail(message)
        message.save(update_fields=['mail_sent'])

        return Response(
            {'detail': 'Nachricht empfangen.'},
            status=status.HTTP_201_CREATED,
        )

    def _client_ip(self, request):
        """Return the client address as forwarded by Nginx."""
        return request.META.get('HTTP_X_REAL_IP') or request.META.get(
            'REMOTE_ADDR'
        )

    def _send_mail(self, message):
        """Send the message and report whether it went out.

        The message is already stored at this point. A failing mail
        server therefore never loses an enquiry, it only leaves
        ``mail_sent`` on False and an entry in the log.
        """
        recipient = getattr(settings, 'CONTACT_RECIPIENT', '')
        if not recipient:
            logger.error("Kontaktformular: CONTACT_RECIPIENT ist nicht "
                         "gesetzt, Nachricht nur gespeichert.")
            return False

        body = (
            f"Neue Nachricht ueber das Kontaktformular\n"
            f"{'-' * 44}\n\n"
            f"Name:     {message.name}\n"
            f"E-Mail:   {message.email}\n"
            f"Zeit:     {message.created_at:%d.%m.%Y %H:%M}\n\n"
            f"Nachricht:\n\n{message.message}\n"
        )

        mail = EmailMessage(
            subject=f"Kontaktanfrage von {message.name}",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[message.email],
        )

        try:
            mail.send(fail_silently=False)
        except Exception:
            logger.exception(
                "Kontaktformular: Versand fehlgeschlagen fuer Nachricht %s",
                message.pk,
            )
            return False

        logger.info("Kontaktformular: Nachricht %s versendet.", message.pk)
        return True

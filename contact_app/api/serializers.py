"""Serializers for the contact app."""

from rest_framework import serializers

from contact_app.models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    """Validates a contact form submission.

    The ``website`` field is a honeypot. It is never shown to a human
    visitor, so anything a client sends in it marks the submission as
    automated. The view decides what to do with that, the serializer
    only passes it through.
    """

    website = serializers.CharField(
        required=False, allow_blank=True, write_only=True,
    )

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'message', 'website')

    def validate_name(self, value):
        """Reject names shorter than three characters."""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "Bitte gib einen Namen mit mindestens 3 Zeichen an."
            )
        return value

    def validate_message(self, value):
        """Reject empty or overly short messages."""
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError(
                "Bitte schreib eine Nachricht mit mindestens 10 Zeichen."
            )
        return value

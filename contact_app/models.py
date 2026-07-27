"""Database models for the contact app."""

from django.db import models


class ContactMessage(models.Model):
    """A message submitted through the portfolio contact form.

    Every submission is stored before the mail is sent, so a failing
    mail server never causes a lost enquiry.
    """

    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(max_length=2500)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    mail_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Kontaktnachricht"
        verbose_name_plural = "Kontaktnachrichten"

    def __str__(self):
        """Return sender and date as the message label."""
        return f"{self.name} <{self.email}> am {self.created_at:%d.%m.%Y}"

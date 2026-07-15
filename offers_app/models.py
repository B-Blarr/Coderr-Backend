"""Database models for the offers app."""

from django.db import models

from auth_app.models import User


class Offer(models.Model):
    """A service offer created by a business user."""

    user = models.ForeignKey(
        User, related_name='user_offers', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to='offers/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        """Return the offer title as its label."""
        return self.title


class OfferDetail(models.Model):
    """A single pricing tier (basic/standard/premium) of an offer."""

    TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ]

    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name="details",
    )
    title = models.CharField(max_length=200)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    class Meta:
        ordering = ['price']

    def __str__(self):
        """Return the detail title as its label."""
        return self.title

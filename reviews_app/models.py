"""Database models for the reviews app."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from auth_app.models import User


class Review(models.Model):
    """A customer's rating and text review of a business user."""

    business_user = models.ForeignKey(
        User, related_name='reviews_as_business', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        User, related_name='reviews_as_reviewer', on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = ['-updated_at']

    def __str__(self):
        """Return the review description as its label."""
        return self.description

"""Database models for the auth app."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with profile fields and a customer/business type."""

    TYPE_CHOICES = [
        ("customer", "Customer"),
        ("business", "Business"),
    ]

    file = models.FileField(upload_to='profiles/', blank=True, null=True)
    location = models.CharField(max_length=200, default="", blank=True)
    tel = models.CharField(max_length=30, default="", blank=True)
    description = models.TextField(default="", blank=True)
    working_hours = models.CharField(max_length=200, default="", blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the username as the user's label."""
        return self.username

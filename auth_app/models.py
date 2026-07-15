from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

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
        return self.username

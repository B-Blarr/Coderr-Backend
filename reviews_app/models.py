from django.db import models
from auth_app.models import User

class Review(models.Model):

    business_user = models.ForeignKey(User, related_name='reviews_as_business')
    reviewer = models.ForeignKey(
        User, related_name='orders_as_reviewer', on_delete=models.CASCADE)
    rating = models.IntegerField(1-9)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = ['-updated_at']

    def __str__(self):
        return self.description

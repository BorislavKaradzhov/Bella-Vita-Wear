from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Override the default email field to force unique emails
    email = models.EmailField(unique=True)
    # Extending the base user with specific fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
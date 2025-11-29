from django.db import models
from django.contrib.auth.models import AbstractUser

class user(AbstractUser):
    username = None
    phone = models.CharField(max_length=15, unique=True) #e.g., +254123456789
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone
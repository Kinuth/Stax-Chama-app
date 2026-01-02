from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=20, unique=True)

from django.db import models
from django.conf import settings

class ChamaGroup(models.Model):
    name = models.CharField(max_length=100)
    # This is the line the error is complaining about:
    chairman = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='led_chamas'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chama_groups')

    def __str__(self):
        return self.name
    
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChamaGroup, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False) # For invitations
    joined_at = models.DateTimeField(auto_now_add=True)

class Contribution(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChamaGroup, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Loan(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('PAID', 'Paid')]
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChamaGroup, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.FloatField(default=10.0) # Fixed 10% for MVP
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_repayment(self):
        return float(self.amount) * (1 + (self.interest_rate / 100))

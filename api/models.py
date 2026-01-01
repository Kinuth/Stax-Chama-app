from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=20, unique=True)

class ChamaGroup(models.Model):
    name = models.CharField(max_length=100)
    chairman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chaired_groups')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

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

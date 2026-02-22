from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    RISK_APPETITE_CHOICES = [
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('aggressive', 'Aggressive'),
    ]
    risk_appetite = models.CharField(
        max_length=20,
        choices=RISK_APPETITE_CHOICES,
        null=True,
        blank=True
    )

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)
    created_at = models.DateTimeField(auto_now_add=True)

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    created_at = models.DateTimeField(auto_now_add=True)
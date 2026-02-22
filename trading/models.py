from django.db import models
from django.conf import settings
from decimal import Decimal

class Transaction(models.Model):
    ACTION_CHOICES = [('BUY', 'Buy'), ('SELL', 'Sell')]
    ORDER_TYPE_CHOICES = [('MARKET', 'Market'), ('LIMIT', 'Limit'), ('STOP_LOSS', 'Stop Loss')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    ticker = models.CharField(max_length=20)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField()
    price_at_execution = models.DecimalField(max_digits=12, decimal_places=2)
    brokerage = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=14, decimal_places=2)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='MARKET')
    pnl = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} | {self.action} {self.quantity} {self.ticker} @ {self.price_at_execution}"


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('LIMIT_BUY', 'Limit Buy'),
        ('LIMIT_SELL', 'Limit Sell'),
        ('STOP_LOSS', 'Stop Loss'),
    ]
    STATUS_CHOICES = [('PENDING', 'Pending'), ('EXECUTED', 'Executed'), ('CANCELLED', 'Cancelled')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    ticker = models.CharField(max_length=20)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    target_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} | {self.order_type} {self.quantity} {self.ticker} @ {self.target_price} [{self.status}]"


class PortfolioPosition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='positions')
    ticker = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField()
    avg_buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'ticker')

    def __str__(self):
        return f"{self.user} | {self.ticker} × {self.quantity} @ avg {self.avg_buy_price}"
    
class PortfolioSnapshot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='snapshots')
    date = models.DateField()
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2)
    invested_value = models.DecimalField(max_digits=15, decimal_places=2)
    daily_pnl = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.user.username} | {self.date} | ₹{self.total_value}"
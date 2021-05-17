from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)

class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True)

class Transaction(models.Model):

    transaction_type_choice = (
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=transaction_type_choice)
    asset_name = models.CharField(max_length=200)
    amount = models.FloatField(default=0)
    price_per_coin = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def __str__(self):
        return str(self.transaction_type)
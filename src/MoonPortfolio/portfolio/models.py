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
    asset_name = asset_name = models.CharField(max_length=200)
    total_asset_amount = models.FloatField(default=0)
    total_asset_price = models.FloatField(default=0)
    current_value = models.FloatField(default=0)


class Transaction(models.Model):

    transaction_type_choice = (
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=transaction_type_choice)
    transaction_date = models.DateTimeField(null=True, blank=True)
    asset_name = models.CharField(max_length=200)
    amount = models.FloatField(default=0)
    price_per_coin = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def __str__(self):
        return str(self.transaction_type)

class Coin(models.Model):

    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=5)
    current_price = models.FloatField(default=0)
    rank = models.IntegerField(default=0)
    market_cap = models.FloatField(default=0)
    image = models.URLField()
    price_change_24h = models.FloatField(default=0, null=True, blank=True)
    price_change_percentage_24h = models.FloatField(default=0, null=True, blank=True)
    circulating_supply = models.FloatField(default=0, null=True, blank=True)
    total_supply = models.FloatField(default=0, null=True, blank=True)
    ath = models.FloatField(default=0, null=True, blank=True)
    atl = models.FloatField(default=0, null=True, blank=True)
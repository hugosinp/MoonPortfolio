from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=1)
    transaction_type = models.CharField(max_length=200)
    asset_name = models.CharField(max_length=200)
    price = models.FloatField()

    def __str__(self):
        return str(self.transaction_type)
from django import forms
from .models import Portfolio, Transaction

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']
        labels = {
            "name" : "Portfolio Name",
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'asset_name', 'amount', 'price_per_coin']
        labels = {
            "transaction_type" : "Transaction Type",
            "asset_name" : "Asset name",
            "amount" : "Coin Amount",
            "price_per_coin" : "Price Per Coin",
        }
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
        
        transaction_date = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'])

        fields = ['transaction_type', 'asset_name', 'amount', 'price_per_coin', 'transaction_date']
        labels = {
            "transaction_type" : "Transaction Type",
            "asset_name" : "Asset",
            "amount" : "Quantity",
            "price_per_coin" : "Price Per Coin",
            "transaction_date" : "Date",
        }


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField
import requests

import json

from .models import Holding, Portfolio, Transaction, Coin

from .forms import PortfolioForm, TransactionForm

@login_required(login_url='login')
def dashboard(request):
    
    portfolios = Portfolio.objects.all().filter(user=request.user)

    form = PortfolioForm()

    if request.method == 'POST':

        form = PortfolioForm(request.POST)

        if form.is_valid():

            instance = form.save()
            instance.user = request.user
            instance.save()

            return redirect('dashboard/'+instance.name)

    else:
        form = PortfolioForm()

    context = {'form' : form, 'portfolios': portfolios}

    return render(request, 'portfolio/dashboard.html', context)


@login_required(login_url='login')
def dashboard2(request, portfolio_name):

    #CoinGecko API URL
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    coin_api = requests.get(url)
    
    #Creating or Updating Coin Data
    for coin in coin_api.json():

        this_coin = Coin.objects.filter(symbol = coin["symbol"].upper())

        if this_coin.exists():
            this_coin.update(
                current_price=coin["current_price"], 
                rank=coin["market_cap_rank"],
                market_cap=coin["market_cap"], 
                image=coin["image"], 
                price_change_24h=coin["price_change_24h"], 
                price_change_percentage_24h=coin["price_change_percentage_24h"],
                circulating_supply=coin["circulating_supply"], 
                total_supply=coin["total_supply"], 
                ath=coin["ath"], 
                atl=coin["atl"]
                )
            
        else:
            coin_record = Coin.objects.create(
                name=coin["name"], 
                symbol=coin["symbol"].upper(), 
                current_price=coin["current_price"], 
                rank=coin["market_cap_rank"], 
                market_cap=coin["market_cap"], 
                image=coin["image"], 
                price_change_24h=coin["price_change_24h"],
                price_change_percentage_24h=coin["price_change_percentage_24h"],
                circulating_supply=coin["circulating_supply"], 
                total_supply=coin["total_supply"], 
                ath=coin["ath"], 
                atl=coin["atl"]
            )

    #All portfolios data
    all_portfolio = Portfolio.objects.all()
    #All current user portfolios
    user_portfolios = Portfolio.objects.all().filter(user=request.user)
    #Current portfolio data
    current_portfolio = Portfolio.objects.filter(user=request.user).get(name=portfolio_name)
    
    #All current portfolio transactions
    transactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id)

    #All current portfolio holdings
    user_holdings = Holding.objects.filter(portfolio_id = current_portfolio)

    #Amount sum order by asset_name (total amount per coin)
    amount_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('amount')).filter(portfolio_id=current_portfolio.id)
    #Price sum order by asset_name (total price per coin)
    price_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('total')).filter(portfolio_id=current_portfolio.id)

    #Total invested sum
    total_invested = Transaction.objects.filter(portfolio_id=current_portfolio.id).aggregate(Sum('total'))
    #Total invested sum
    current_balance = Holding.objects.filter(portfolio_id=current_portfolio.id).aggregate(Sum('current_value'))

    #All coin data
    coin_data = Coin.objects.all()
    

    #Updates or creates the total asset amount in Holding Table
    for amount in amount_sum_per_coin:
        this_holding = Holding.objects.filter(portfolio_id = current_portfolio).filter(asset_name = amount['asset_name'])

        if this_holding.exists():
            this_holding.filter(asset_name = amount['asset_name']).update(
                total_asset_amount = amount['amount__sum'],
            )

        else:
            holding_record = Holding.objects.create(
                portfolio=current_portfolio,
                asset_name=amount['asset_name'],
                total_asset_amount = amount['amount__sum'], 
            )

    #Updates the total price amount in Holding Table
    for price in price_sum_per_coin:
        this_holding = Holding.objects.filter(portfolio_id = current_portfolio).filter(asset_name = price['asset_name'])

        if this_holding.exists():
            this_holding.filter(asset_name = price['asset_name']).update(
                total_asset_price = price['total__sum']
            )

    #Updates the asset current value (total_asset_amount*asset current price)
    for coin in coin_data:
        user_holdings.filter(asset_name=coin.symbol).update(
            current_value = F('total_asset_amount') * coin.current_price
        )

    #Pie chart Data
    asset_names = []
    holdings_percentages = []

    for holding in user_holdings:
        asset_names.append(holding.asset_name)

        if current_balance['current_value__sum'] is None:
            percentage = 100
            holdings_percentages.append(percentage)
        elif current_balance['current_value__sum'] != 0:
            percentage = holding.current_value/current_balance['current_value__sum']*100
            holdings_percentages.append(percentage)


    #Transaction Form
    form = TransactionForm()

    if request.method == 'POST':

        form = TransactionForm(request.POST)

        if form.is_valid():

            instance = form.save()

            instance.portfolio = current_portfolio
            if instance.transaction_type == "Buy":
                instance.total = instance.amount * instance.price_per_coin
            elif instance.transaction_type == "Sell":
                negative_amount = "-"+str(instance.amount)
                negative_total = "-"+str(instance.amount)
                instance.amount = float(negative_amount)
                instance.total = float(negative_total)
                instance.total = instance.amount * instance.price_per_coin
                
            instance.save()

            return redirect('/portfolio/dashboard/'+current_portfolio.name)

    else:
        form = TransactionForm()


    context = {
                'form': form,
                'all_portfolio': all_portfolio,
                'current_portfolio': current_portfolio, 
                'transactions': transactions, 
                'asset_names': asset_names,
                'holdings_percentages': holdings_percentages,
                'user_holdings': user_holdings,
                'current_balance': current_balance,
                'total': total_invested,
                'coin_data': coin_data
            }

    return render(request, 'portfolio/indepth_dashboard.html', context)
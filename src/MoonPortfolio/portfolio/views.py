from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField
import requests

import json

from .models import Portfolio, Transaction

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
    coin_data = requests.get(url)

    #All portfolios data
    all_portfolio = Portfolio.objects.all()

    #All current user portfolios
    user_portfolios = Portfolio.objects.all().filter(user=request.user)

    #Current portfolio data
    current_portfolio = Portfolio.objects.filter(user=request.user).get(name=portfolio_name)
    
    #All current portfolio transactions
    transactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id)

    #All current portfolio transactions
    stransactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id).values("asset_name").distinct()

    #Amount sum order by asset_name (total amount per coin)
    amount_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('amount')).filter(portfolio_id=current_portfolio.id)
    
    #Price sum order by asset_name (total price per coin)
    price_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('total')).filter(portfolio_id=current_portfolio.id)

    #Total invested sum
    total = Transaction.objects.filter(portfolio_id=current_portfolio.id).aggregate(Sum('total'))
    
    entry_list = list(stransactions)
    print(entry_list)

    for s in entry_list:
        print(s)
        
    prices = {}

    for coin in coin_data.json():
        prices[coin["symbol"]] = coin["current_price"]
    """
    for s in prices.keys():
        if s == entry_list.lower():
            print("output")
            print(prices.get(entry_list.lower()))
    """
    #Pie chart Data
    assets = []
    percentages = []
    totals = 0

    for key, value in total.items():
        if key == 'total__sum':
            totals = value

    for asset in price_sum_per_coin:
        for key, value in asset.items():
            if key == 'asset_name':
                assets.append(value)
            elif key == 'total__sum':
                if totals != 0:
                    value = (value/totals)*100
                    percentages.append(value)
                elif totals == 0:
                    totals = 100
                    value = (value/totals)*100
                    percentages.append(value)


    #Transaction Form
    form = TransactionForm()

    if request.method == 'POST':

        form = TransactionForm(request.POST)

        if form.is_valid():

            instance = form.save()
            instance.portfolio = current_portfolio
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
                'amount_sum_per_coin': amount_sum_per_coin, 
                'price_sum_per_coin': price_sum_per_coin, 
                'total': total,
                'assets': assets,
                'percentages': percentages,
                'coin_data': coin_data
            }

    return render(request, 'portfolio/indepth_dashboard.html', context)
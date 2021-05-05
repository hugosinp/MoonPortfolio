from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField
import requests

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

    all_portfolio = Portfolio.objects.all()
    portfolio_data = Portfolio.objects.get(name=portfolio_name)
    transactions = Transaction.objects.all().filter(portfolio_id=portfolio_data.id)

    amount_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('amount')).filter(portfolio_id=portfolio_data.id)
    price_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('total')).filter(portfolio_id=portfolio_data.id)
    total = Transaction.objects.aggregate(Sum('total'))
    #date jour-mois-année
    #data = "https://api.coingecko.com/api/v3/coins/"+coin_name+"/history?date="+date+"&localization=false"
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    coin_data = requests.get(url).json

    labels = []
    data = []
    totals = 0

    for key, value in total.items():
        if key == 'total__sum':
            totals = value

    for asset in price_sum_per_coin:
        for key, value in asset.items():
            if key == 'asset_name':
                labels.append(value)
            elif key == 'total__sum':
                if totals != 0:
                    value = (value/totals)*100
                    data.append(value)
                elif totals == 0:
                    totals = 100
                    value = (value/totals)*100
                    data.append(value)

    print(totals)

    form = TransactionForm()

    if request.method == 'POST':

        form = TransactionForm(request.POST)

        if form.is_valid():

            instance = form.save()
            instance.portfolio = portfolio_data
            instance.total = instance.amount * instance.price_per_coin
            instance.save()

            return redirect('/portfolio/dashboard/'+portfolio_data.name)

    else:
        form = TransactionForm()

    context = {
                'form': form,
                'all_portfolio': all_portfolio,
                'portfolio_data': portfolio_data, 
                'transactions': transactions, 
                'amount_sum_per_coin': amount_sum_per_coin, 
                'price_sum_per_coin': price_sum_per_coin, 
                'total': total,
                'labels': labels,
                'data': data,
                'coin_data': coin_data
            }

    return render(request, 'portfolio/indepth_dashboard.html', context)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField

from .models import Portfolio, Transaction

from .forms import PortfolioForm

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

    portfolio_data = Portfolio.objects.get(name=portfolio_name)
    transactions = Transaction.objects.all().filter(portfolio_id=portfolio_data.id)

    amount_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('amount'))
    price_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('total'))
    total = Transaction.objects.aggregate(totally=Sum('total'))
    #date jour-mois-année
    #data = "https://api.coingecko.com/api/v3/coins/"+coin_name+"/history?date="+date+"&localization=false"

    context = {'portfolio_data': portfolio_data, 'transactions': transactions, 'amount_sum_per_coin': amount_sum_per_coin, 'price_sum_per_coin': price_sum_per_coin, 'total': total}
    print(context)
    return render(request, 'portfolio/indepth_dashboard.html', context)
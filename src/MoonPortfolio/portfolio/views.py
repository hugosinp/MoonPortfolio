from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Portfolio, Transaction

from .forms import PortfolioForm

@login_required(login_url='login')
def dashboard(request):
    
    portfolios = Portfolio.objects.all().filter(user=request.user)

    if portfolios is None:

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

        context = {'form' : form}

        return render(request, 'portfolio/dashboard.html', context)
    
    else:
        
        context = {'portfolios': portfolios}

        return render(request, 'portfolio/dashboard.html', context)


@login_required(login_url='login')
def dashboard2(request, portfolio_name):

    portfolio_data = Portfolio.objects.get(name=portfolio_name)
    transactions = Transaction.objects.all().filter(portfolio_id=portfolio_data.id)
    context = {'portfolio_data': portfolio_data, 'transactions': transactions}

    print(context)
    return render(request, 'portfolio/indepth_dashboard.html', context)
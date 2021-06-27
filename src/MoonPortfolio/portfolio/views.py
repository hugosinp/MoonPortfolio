from portfolio.functions import avg_buy_price, coin_performance, get_coin_api, get_gainers_losers, get_piechart_data, update_coin_data, update_holding_data

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Holding, Portfolio, Transaction, Coin
from .forms import PortfolioForm, TransactionForm

@login_required(login_url='login')
def dashboard_selection(request):

    """=========================================QUERY SECTION========================================="""

    coin_data = get_coin_api(True)

    portfolios = Portfolio.objects.all().filter(user=request.user)

    """=========================================ON LOAD SECTION========================================="""

    gainers = get_gainers_losers()[0]
    losers = get_gainers_losers()[1]

    """=========================================FORM SECTION========================================="""
    portfolio_form = PortfolioForm()

    if request.method == 'POST':

        portfolio_form = PortfolioForm(request.POST)

        if portfolio_form.is_valid():

            instance = portfolio_form.save()
            instance.user = request.user
            instance.save()

            return redirect('dashboard/'+str(instance.id))

    else:
        portfolio_form = PortfolioForm()


    context = {
                'portfolio_form' : portfolio_form,
                'portfolios': portfolios,
                'coin_data': coin_data,
                'gainers_dict_list': gainers[0:4],
                'losers_dict_list': losers[0:4],
            }

    return render(request, 'portfolio/dashboard.html', context)


@login_required(login_url='login')
def dashboard(request, portfolio_id):
    """Render the portfolio dashboard

    Args:
        request ([type]): [description]
        portfolio_id ([type]): [description]

    Returns:
        [type]: [description]
    """

    """=========================================QUERY SECTION========================================="""
    #Returns all Current User Portfolios from Portfolio Table
    user_portfolios = Portfolio.objects.all().filter(user=request.user)

    #Returns the Current Portfolio from Portfolio Table
    current_portfolio = Portfolio.objects.get(id=portfolio_id)

    #Returns all the holdings from the current Portfolio
    user_holdings = Holding.objects.all().filter(portfolio_id=current_portfolio)

    #Returns all the current portfolio transactions
    transactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id)

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

    """=========================================ON LOAD SECTION========================================="""
    if request.user == current_portfolio.user :

        #Creates or Updates Coin Data
        update_coin_data()

        #Creates or Updates Holding Data
        update_holding_data(current_portfolio, user_holdings, amount_sum_per_coin, price_sum_per_coin, coin_data)

        #Creates or Updates Pie chart Data
        pie_chart_data = get_piechart_data(user_holdings, current_balance)

        #Creates or Updates Top/Worst coin Performance
        coin_performance(portfolio_id, user_portfolios, user_holdings , price_sum_per_coin)

        #Creates or Updates assets average buy price
        avg_buy_price(portfolio_id)

        #Formatting Transactions Dates
        for transaction in transactions:
            transaction.transaction_date = transaction.transaction_date.strftime('%m/%d/%Y')

        #Transactions dict into a reversed list to get last transactions
        last_transactions = list(reversed(list(transactions)))


        """=========================================FORM SECTION========================================="""
        #Transaction Form
        transaction_form = TransactionForm()

        if request.method == 'POST':

            transaction_form = TransactionForm(request.POST)

            if transaction_form.is_valid():

                instance = transaction_form.save()

                instance.portfolio = current_portfolio
                if instance.transaction_type == "Buy":
                    instance.total = instance.amount * instance.price_per_coin
                elif instance.transaction_type == "Sell":
                    negative_amount = "-"+str(instance.amount)
                    negative_total = "-"+str(instance.amount)
                    instance.amount = float(negative_amount)
                    instance.total = float(negative_total)
                    instance.total = instance.amount * instance.price_per_coin
                
                try:
                    this_holding = user_holdings.get(asset_name=instance.asset_name)
                    print("this holding exists")
                    instance.save()
                    return redirect('/portfolio/dashboard/'+str(current_portfolio.id))

                except:
                    holding_record = Holding.objects.create(
                        portfolio=current_portfolio,
                        asset_name=instance.asset_name,
                        total_asset_amount=instance.amount,
                    )

                    instance.holding=holding_record
                    instance.save()

                    return redirect('/portfolio/dashboard/'+str(current_portfolio.id))

        else:
            transaction_form = TransactionForm()

        #Portfolio Creation Form
        portfolio_form = PortfolioForm()

        if request.method == 'POST':

            portfolio_form = PortfolioForm(request.POST)

            if portfolio_form.is_valid():

                instance = portfolio_form.save()
                instance.user = request.user
                instance.save()

                return redirect('/portfolio/dashboard/'+str(instance.id))

        else:
            portfolio_form = PortfolioForm()


        #Portfolio Modify Form
        portfolio_modify_form = PortfolioForm()
        
        if request.method == 'POST':
            instance = Portfolio.objects.get(id=portfolio_id)
            portfolio_modify_form = PortfolioForm(request.POST, instance=instance)

            if portfolio_modify_form.is_valid():

                portfolio_modify_form.save()

                return redirect('/portfolio/dashboard')

        else:
            portfolio_modify_form = PortfolioForm()

        context = {
                    'current_balance': current_balance,
                   'transaction_form': transaction_form,
                    'portfolio_form': portfolio_form,
                    'portfolio_modify_form': portfolio_modify_form,
                    'user_portfolios': user_portfolios,
                    'current_portfolio': current_portfolio, 
                    'transactions': last_transactions,
                    'last_transactions': last_transactions[0:5], 
                    'asset_names': pie_chart_data[0],
                    'holdings_percentages': pie_chart_data[1],
                    'user_holdings': user_holdings,
                    'total': total_invested,
                    'coin_data': coin_data
                }

        return render(request, 'portfolio/indepth_dashboard.html', context)  


@login_required(login_url='login')
def edit_portfolio(request, portfolio_id):

    this_portofolio = Portfolio.objects.get(id=portfolio_id)

    return redirect('/portfolio/dashboard')


@login_required(login_url='login')
def delete_portfolio(request, portfolio_id):

    this_portofolio = Portfolio.objects.get(id=portfolio_id)

    if request.user == this_portofolio.user:

        this_portofolio.delete()

        return redirect('/portfolio/dashboard')


@login_required(login_url='login')
def delete_transaction(request, portfolio_id, holding_id, transaction_id):

    this_portofolio = Portfolio.objects.get(id=portfolio_id)
    this_transaction = Transaction.objects.get(id=transaction_id)

    if request.user == this_portofolio.user:
        this_transaction.delete()
        
        #All current portfolio transactions
        transactions = Transaction.objects.filter(portfolio_id=this_portofolio).filter(holding_id=holding_id)

        print(transactions)

        if transactions.exists():
            print("this holding exists and is not empty")

            return redirect('/portfolio/dashboard/'+str(portfolio_id)+'/'+str(holding_id))

        else:
            obsolete_holding = Holding.objects.get(id=holding_id)
            obsolete_holding.delete()

            return redirect('/portfolio/dashboard/'+str(portfolio_id))



@login_required(login_url='login')
def holding_details(request, portfolio_id, holding_id):
    """[summary]

    Args:
        request ([type]): [description]
        portfolio_id ([type]): [description]
        holding_id ([type]): [description]

    Returns:
        [type]: [description]
    """

    """=========================================QUERY SECTION========================================="""
    #Returns the coin API as JSON
    coin_api = get_coin_api(True)

    #Returns all coins from Coin Table
    coin_data = Coin.objects.all()

    #Returns all Current User Portfolios from Portfolio Table
    user_portfolios = Portfolio.objects.all().filter(user=request.user)

    #Returns the Current Portfolio from Portfolio Table
    current_portfolio = Portfolio.objects.get(id=portfolio_id)

    #Returns all the holdings from the current Portfolio
    user_holdings = Holding.objects.all().filter(portfolio_id=current_portfolio)

    #Returns the holding by ID
    current_holding = Holding.objects.get(id=holding_id)

    #Returns all the transactions from the current Portfolio
    holding_transactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id).filter(asset_name=current_holding.asset_name)

    #Price sum order by asset_name (total price per coin)
    price_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('total')).filter(portfolio_id=current_portfolio.id)
    #Amount sum order by asset_name (total amount per coin)
    amount_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('amount')).filter(portfolio_id=current_portfolio.id)

    """=========================================QUERY SECTION========================================="""
    if request.user == current_portfolio.user:

        update_holding_data(current_portfolio, user_holdings, amount_sum_per_coin, price_sum_per_coin, coin_data)

        #Profit/Loss
        initial = 0.0

        for price in price_sum_per_coin:
            if(current_holding.asset_name == price['asset_name']):
                initial = price['total__sum']

        profit_loss = current_holding.current_value - initial

        date = []
        amount = []
        total_price = []

        for holding in holding_transactions:
            date.append(holding.transaction_date.strftime('%m/%d/%Y'))
            amount.append(holding.amount)
            total_price.append(holding.total)


        """=========================================FORM SECTION========================================="""
        #Transaction Form
        transaction_form = TransactionForm()

        if request.method == 'POST':

            transaction_form = TransactionForm(request.POST)

            if transaction_form.is_valid():

                instance = transaction_form.save()

                instance.portfolio = current_portfolio
                if instance.transaction_type == "Buy":
                    instance.total = instance.amount * instance.price_per_coin
                elif instance.transaction_type == "Sell":
                    negative_amount = "-"+str(instance.amount)
                    negative_total = "-"+str(instance.amount)
                    instance.amount = float(negative_amount)
                    instance.total = float(negative_total)
                    instance.total = instance.amount * instance.price_per_coin
                
                try:
                    this_holding = user_holdings.get(asset_name=instance.asset_name)
                    print("this holding exists")
                    instance.save()
                    return redirect('/portfolio/dashboard/'+str(current_portfolio.id))

                except:
                    holding_record = Holding.objects.create(
                        portfolio=current_portfolio,
                        asset_name=instance.asset_name,
                        total_asset_amount=instance.amount,
                    )

                    instance.holding=holding_record
                    instance.save()

                    return redirect('/portfolio/dashboard/'+str(current_portfolio.id))

        else:
            transaction_form = TransactionForm()

        context = {
            'user_portfolios': user_portfolios,
            'current_portfolio': current_portfolio, 
            'user_holdings': user_holdings,
            'current_holding': current_holding,
            'holding_transactions': holding_transactions,
            'profit_loss': profit_loss,
            'initial': initial,
            'transaction_form': transaction_form,
            'coin_api': coin_api,
            'date': date,
            'total_price': total_price,
            'amount': amount
        }

        return render(request, 'portfolio/holding.html', context)
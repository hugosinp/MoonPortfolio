from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
import requests

import json
import heapq

from .models import Holding, Portfolio, Transaction, Coin
from .forms import PortfolioForm, TransactionForm

@login_required(login_url='login')
def dashboard_selection(request):

    #CoinGecko API URL
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    coin_api = requests.get(url)
    coin_data = requests.get(url).json()

    portfolios = Portfolio.objects.all().filter(user=request.user)

    input_list = []

    gainers_dict_list = []
    losers_dict_list = []

    for coin in coin_api.json():

        input_list.append(coin['price_change_percentage_24h'])
        number_of_elements = 5
        largest_list = heapq.nlargest(number_of_elements, input_list)
        smallest_list = heapq.nsmallest(number_of_elements, input_list)
        

    for coin in coin_api.json():
        for largest in largest_list:
            if largest == coin['price_change_percentage_24h']:
                this_dict = {
                    "asset_name": coin['name'],
                    "symbol": coin['symbol'],
                    "current_price": coin['current_price'],
                    "price_change_percentage_24h": coin['price_change_percentage_24h']
                }
                
                gainers_dict_list.append(this_dict)

        for smallest in smallest_list:
            if smallest == coin['price_change_percentage_24h']:
                this_dict = {
                    "asset_name": coin['name'],
                    "symbol": coin['symbol'],
                    "current_price": coin['current_price'],
                    "price_change_percentage_24h": coin['price_change_percentage_24h']
                }
                
                losers_dict_list.append(this_dict)

    gainers_dict_list = sorted(gainers_dict_list, key = lambda i: i['price_change_percentage_24h'],reverse=True)
    losers_dict_list = sorted(losers_dict_list, key = lambda i: i['price_change_percentage_24h'],reverse=False)

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
                'gainers_dict_list': gainers_dict_list[0:5],
                'losers_dict_list': losers_dict_list[0:5],
            }

    return render(request, 'portfolio/dashboard.html', context)


@login_required(login_url='login')
def dashboard(request, portfolio_id):

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

    #All current user portfolios
    user_portfolios = Portfolio.objects.all().filter(user=request.user)

    #Current portfolio data
    current_portfolio = Portfolio.objects.get(id=portfolio_id)
    
    #All current portfolio transactions
    transactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id)

    #All current portfolio holdings
    user_holdings = Holding.objects.all().filter(portfolio_id=current_portfolio)

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
    

    if request.user == current_portfolio.user :

        #Updates or creates the total asset amount in Holding Table
        for amount in amount_sum_per_coin:
            this_holding = Holding.objects.filter(portfolio_id = current_portfolio).filter(asset_name = amount['asset_name'])

            if this_holding.exists():
                this_holding.filter(asset_name = amount['asset_name']).update(
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


        #Formatting Transactions Dates
        for transaction in transactions:
            transaction.transaction_date = transaction.transaction_date.strftime('%m/%d/%Y')

        #Transactions dict into a reversed list to get last transactions
        last_transactions = list(reversed(list(transactions)))

        #Profit/Loss
        initial = 0.0
        coin_performance_dict = {}

        for price in price_sum_per_coin:
            for holding in user_holdings:
                if(holding.asset_name == price['asset_name']):
                    initial = price['total__sum']
                    profit_loss = holding.current_value - initial

                    coin_performance_dict.update({holding.asset_name: profit_loss})

        #Check if coin_performance_dict is empty
        if not coin_performance_dict:
            print("Empty dict")
        
        else:
            maximum = max(coin_performance_dict, key=coin_performance_dict.get)
            minimum = min(coin_performance_dict, key=coin_performance_dict.get)

            #Updating the min and max to the Portfolio table
            user_portfolios.filter(id=portfolio_id).update(top_performance_name=maximum)
            user_portfolios.filter(id=portfolio_id).update(top_performance_value=coin_performance_dict[maximum])
            user_portfolios.filter(id=portfolio_id).update(worst_performance_name=minimum)
            user_portfolios.filter(id=portfolio_id).update(worst_performance_value=coin_performance_dict[minimum])

        context = {
                    'transaction_form': transaction_form,
                    'portfolio_form': portfolio_form,
                    'portfolio_modify_form': portfolio_modify_form,
                    'user_portfolios': user_portfolios,
                    'current_portfolio': current_portfolio, 
                    'transactions': last_transactions,
                    'last_transactions': last_transactions[0:5], 
                    'asset_names': asset_names,
                    'holdings_percentages': holdings_percentages,
                    'user_holdings': user_holdings,
                    'current_balance': current_balance,
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

    #All coin data
    coin_data = Coin.objects.all()

    #All current user portfolios
    user_portfolios = Portfolio.objects.all().filter(user=request.user)

    #Current portfolio data
    current_portfolio = Portfolio.objects.get(id=portfolio_id)

    #All current portfolio holdings
    user_holdings = Holding.objects.all().filter(portfolio_id = current_portfolio)

    current_holding = Holding.objects.get(id=holding_id)

    #All current holding transactions
    holding_transactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id).filter(asset_name=current_holding.asset_name)

    #Price sum order by asset_name (total price per coin)
    price_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('total')).filter(portfolio_id=current_portfolio.id)
    #Amount sum order by asset_name (total amount per coin)
    amount_sum_per_coin = Transaction.objects.values('asset_name').annotate(Sum('amount')).filter(portfolio_id=current_portfolio.id)


    if request.user == current_portfolio.user:

        #Updates or creates the total asset amount in Holding Table
        for amount in amount_sum_per_coin:
            this_holding = Holding.objects.filter(portfolio_id = current_portfolio).filter(asset_name = amount['asset_name'])

            if this_holding.exists():
                this_holding.filter(asset_name = amount['asset_name']).update(
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
                    
                instance.save()

                return redirect('/portfolio/dashboard/'+str(current_portfolio.id)+'/'+str(holding_id))

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

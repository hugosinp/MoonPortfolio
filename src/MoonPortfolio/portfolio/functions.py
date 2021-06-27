from django.shortcuts import redirect
from portfolio.forms import TransactionForm

from django.db.models.aggregates import Avg
from django.db.models.expressions import F
from portfolio.models import Coin, Holding, Portfolio, Transaction

import requests
import heapq

def get_coin_api(json):
    """Returns the Coin API

    Args:
        json ([Bool]): if True return the coin API in JSON format
    """

    #CoinGecko API URL
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    
    if json == True:
        coin_api = requests.get(url).json()

    elif json == False:
        coin_api = requests.get(url)

    return coin_api

def get_gainers_losers():
    input_list = []
    gainers_dict_list = []
    losers_dict_list = []

    for coin in get_coin_api(True):

        input_list.append(coin['price_change_percentage_24h'])
        number_of_elements = 4
        largest_list = heapq.nlargest(number_of_elements, input_list)
        smallest_list = heapq.nsmallest(number_of_elements, input_list)
        

    for coin in get_coin_api(True):
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

    return gainers_dict_list, losers_dict_list


def update_coin_data():

    """Update the coin data"""

    for coin in get_coin_api(True):

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


def update_holding_data(current_portfolio, user_holdings, amount_sum_per_coin, price_sum_per_coin, coin_data):
    
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

    #Updates the asset current value (total_asset_amount*asset current price) in the Holding Table
    for coin in coin_data:
        user_holdings.filter(asset_name=coin.symbol).update(
            current_value = F('total_asset_amount') * coin.current_price
        )


def coin_performance(portfolio_id, user_portfolios, user_holdings , price_sum_per_coin):

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


def get_piechart_data(user_holdings, current_balance):
    
    """Asset pie chart"""
    
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

    return asset_names, holdings_percentages


def avg_buy_price(portfolio_id):

    """Average buy price Function"""

    #Current portfolio data
    current_portfolio = Portfolio.objects.get(id=portfolio_id)

    #All current portfolio transactions
    transactions = Transaction.objects.all().filter(portfolio_id=current_portfolio.id)

    for transaction in transactions:
        avg = Transaction.objects.all().filter(asset_name=transaction.asset_name).aggregate(Avg('price_per_coin'))
        print(avg)

        Holding.objects.filter(portfolio_id=current_portfolio).filter(asset_name = transaction.asset_name).update(
            average_buy_price = avg['price_per_coin__avg']
            )
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Asset

import requests


@login_required(login_url='login')
def market_simplified(request):

    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    data = requests.get(url).json

    context = {'data': data}

    return render(request, 'market/market_simplified.html', context)

@login_required(login_url='login')
def market_advanced(request):

    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    data = requests.get(url).json

    context = {'data': data}

    return render(request, 'market/market_advanced.html', context)

@login_required(login_url='login')
def asset(request, asset_symbol):

    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    data = requests.get(url).json
       
    context = {'data': data, 'asset_symbol': asset_symbol}

    return render(request, 'market/asset.html', context)
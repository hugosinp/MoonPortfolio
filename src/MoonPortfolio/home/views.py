from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import requests


def home(request):
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    data = requests.get(url).json

    context = {'data': data}

    return render(request, 'home/home.html', context)
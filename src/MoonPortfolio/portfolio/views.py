from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):

    context = {}

    return render(request, 'portfolio/dashboard.html', context)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import CreateUserForm

def register(request):
    form = CreateUserForm()

    if (request.method == "POST"):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account '+user+ ' was succesfully created !')

            return redirect('loginPage')

    context = {'form' : form}
    return render(request, 'registration/register.html', context)

def loginPage(request):

    if(request.method == "POST"):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'registration/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('loginPage')


def profilePage(request):

    context = {}
    return render(request, 'registration/profile.html', context)


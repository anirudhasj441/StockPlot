from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def index(request):

    return render(request, 'home/index.html')

# APIs 

def userLogout(request):
    logout(request)
    return redirect("/")

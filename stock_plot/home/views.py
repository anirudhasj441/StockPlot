import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import StockWatchlist
from stock.models import Stock
import yfinance as yf
import logging

logger = logging.getLogger("debug")

# Create your views here.

def index(request):
    params = {
        "watchlists": []
    }
    if request.user.is_authenticated:
        watchlists = StockWatchlist.objects.filter(user=request.user)
        if watchlists:
            watchlist = watchlists[0]
            watchlist_stocks = watchlist.stocks.all()            
            for stock in watchlist_stocks:
                symbol = stock.symbol
                ticker = yf.Ticker(symbol)
                open_price = ticker.info["open"]
                price = ticker.info["currentPrice"]
                print(open_price)
                diff = round(price - open_price, 2)
                stock_data = {
                    "symbol": symbol,
                    "name": stock.full_name,
                    "price": price,
                    "diff": diff,
                    "currency": stock.currency,
                }
                params["watchlists"].append(stock_data)

    return render(request, 'home/index.html', params)

# APIs 

@csrf_exempt
def userSignUp(request):
    response = {}
    if not request.user.is_authenticated:
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                email = data["email"]
                fname = data["fname"]
                lname = data["lname"]
                password = data["password"]
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=fname,
                    last_name=lname
                )
                user.save()
            except Exception as err:
                response["status"] = "failed"
                response["message"] = "Error: " + str(err)
            else:
                response["status"] = "success"
                response["message"] = "Account Created"
    return JsonResponse(response, safe=True)

@csrf_exempt
def userLogin(request):
    response = {}
    if not request.user.is_authenticated:
        if request.method == "POST":
            data = json.loads(request.body)
            email = data["email"]
            password = data["password"]
            user = authenticate(
                username=email,
                password=password
            )
            if user is not None:
                login(request, user)
                response["status"] = "success"
            else:
                response["status"] = "failed"
                response["message"] = "Invalid Credentials!"
    return JsonResponse(response, safe=True)

def userLogout(request):
    logout(request)
    return redirect("/")

@csrf_exempt
def addToWatchlist(request):
    try:
        response = {}
        if request.user.is_authenticated:
            data = json.loads(request.body)
            print(data)
            symbol = data["symbol"]
            stock = Stock.objects.get(symbol=symbol)
            watchlists = StockWatchlist.objects.filter(user=request.user)
            if not watchlists:
                watchlist = StockWatchlist.objects.create(
                    user = request.user
                )
                watchlist.stocks.add(stock)
                watchlist.save()
            else:
                watchlist = watchlists[0]
                watchlist.stocks.add(stock)
                watchlist.save()
        else:
            response["status"] = "failed"
            response["message"] = "Please login!!"
    except Exception as e:
        print("Error: ", str(e))
        logger.error("Error: " + str(e))
        response["status"] = "failed"
        response["message"] = "Error: " + str(e)
    else:
        response["status"] = "success"
    finally:
        return JsonResponse(response, safe=False)

@csrf_exempt
def removeFromWatchlist(request):
    try:
        response = {}
        if request.user.is_authenticated:
            data = json.loads(request.body)
            symbol = data["symbol"]
            stock = Stock.objects.get(symbol=symbol)
            watchlists = StockWatchlist.objects.filter(user=request.user)
            if watchlists:
                watchlist = watchlists[0]
                watchlist.stocks.remove(stock)
                watchlist.save()
    except Exception as e:
        response["status"] = "failed"
        response["message"] = "Error: " + str(e)
    else:
        response["status"] = "success"
    finally:
        return JsonResponse(response, safe=False)

@csrf_exempt
def checkStockInWatchlist(request):
    response = {}
    if request.user.is_authenticated:
        data = json.loads(request.body)
        symbol = data["symbol"]
        stock = Stock.objects.get(symbol=symbol)
        watchlists = StockWatchlist.objects.filter(user=request.user)
        if watchlists:
            watchlist = watchlists[0]
            watchlist_stocks = watchlist.stocks.all()
            response["watchlisted"] = stock in watchlist_stocks
            
        response["status"] = "success"
    else:
        response["status"] = "failed"
    
    return JsonResponse(response, safe=False)

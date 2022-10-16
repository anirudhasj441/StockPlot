from locale import currency
from django.shortcuts import render

# Create your views here.

def stock(request):
    symbol = request.GET["symbol"]
    name = request.GET["name"]
    currency = request.GET["currency"]
    params = {
        "symbol": symbol,
        "name": name,
        "currency": currency
    }

    return render(request, "stock/stock.html", params)
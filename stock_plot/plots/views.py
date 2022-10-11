import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
import plotly.graph_objects as go
import plotly.io
import requests


# Create your views here.

def timeseries(request):
    params = {
        "tmp": "temp"
    }
    return render(request, 'plots/timeseries.html', params)

@csrf_exempt
def intraDay(request):
    data = json.loads(request.body)
    sym = data["sym"]
    period = data["period"]
    interval = "5m"
    if period not in ["1d", "5d", "1mo"]:
        interval = "1d"
    data = yf.download(sym, period=period, interval=interval)
    x = data.index
    y = data["Close"]
    trace = go.Scatter(
        x=x,
        y=y,
        connectgaps=True
    )
    layout = go.Layout(
        title="Tata Consultancy Services",
        xaxis={
            "type": "date"
        }
    )
    fig = go.Figure([trace], layout)
    fig_data = json.loads(plotly.io.to_json(fig))
    print(y.iloc[-1])
    fig_data["latest_price"] = y.iloc[-1]
    fig_data["latest_time"] = x[-1]
    return JsonResponse(fig_data, safe=False)


# APIs
@csrf_exempt
def searchSymbols(request):
    data = json.loads(request.body)
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/auto-complete"
    params = {
        "q": data["q"]
    }
    headers = {
        "X-RapidAPI-Key": "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710",
        "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=params).json()
    results = response["quotes"]
    ret = []
    for item in results:
        if item["exchDisp"] == "NSE" and "longname" in item.keys():
            data = {
                "name": item["longname"],
                "symbol": item["symbol"],
                "currency": "INR"
            }
            ret.append(data)
    return JsonResponse(ret, safe=False)

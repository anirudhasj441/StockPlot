import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
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

# APIs
@csrf_exempt
def intraDay(request):
    try:
        data = json.loads(request.body)
        sym = data["sym"]
        period = data["period"]
        interval = "5m"
        if period not in ["1d", "5d", "1mo"]:
            interval = "1d"
        stock_data = yf.download(sym, period=period, interval=interval)
        stock_data.dropna()
        x = stock_data.index
        y = stock_data["Close"]
        if data["chart_type"] == "line_chart":
            trace = go.Scatter(
                x=x,
                y=y,
                line={
                    "color": "#6368C9"
                },
                connectgaps=True
            )
        else:
            trace = go.Candlestick(
                x=x,
                open=stock_data["Open"],
                high=stock_data["High"],
                low=stock_data["Low"],
                close=stock_data["Close"]
            )

        layout = go.Layout(
            title="Tata Consultancy Services",
            xaxis={
                "type": "date"
            }
        )
        fig = go.Figure([trace], layout)
        fig_data = json.loads(plotly.io.to_json(fig))
        fig_data["latest_price"] = y.iloc[-1]
        fig_data["latest_time"] = x[-1]
    except IndexError:
        fig_data["status"] = "failed"
        fig_data["message"] = "Data not fetched!"
    else:
        fig_data["status"] = "success"
    return JsonResponse(fig_data, safe=False)

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

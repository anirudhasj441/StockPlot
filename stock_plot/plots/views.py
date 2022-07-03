import json
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
import yfinance as yf


# Create your views here.

def home(request):
    params = {
        "tmp": "temp"
    }
    return render(request, 'plots/index.html', params)

def intraDay(request):
    df = yf.download("msft", period="1d", interval="5m")
    df = df.reset_index()
    # for i in df:
    #     print(i["High"])
    
    # print(df.to_json(orient="records"))
    data = df.loc[:, ["Datetime", "High"]].to_json(orient="records")
    data = json.loads(data)
    x = []
    y = []
    trace = {}
    for item in data:
        x.append(datetime.fromtimestamp(item["Datetime"] / 1e3))
        y.append(item["High"])
    trace["x"] = x
    trace["y"] = y
    trace["type"] = "scatter"

    return JsonResponse(trace, safe=False)

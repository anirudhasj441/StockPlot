import json
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
import yfinance as yf
import requests


# Create your views here.

def home(request):
    params = {
        "tmp": "temp"
    }
    return render(request, 'plots/index.html', params)

def intraDay(request):
    sym = "TATAPOWER.BSE"
    tc = yf.Ticker(sym)
    df = yf.download(sym, period="1d", interval="5m")
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
    print(tc.info["currency"])

    return JsonResponse(trace, safe=False)

def getTicker (company_name):
    url = "https://s.yimg.com/aq/autoc"
    parameters = {'query': company_name, 'lang': 'en-US'}
    response = requests.get(url = url, params = parameters)
    # data = response.json()
    # company_code = data['ResultSet']['Result'][0]['symbol']
    return response

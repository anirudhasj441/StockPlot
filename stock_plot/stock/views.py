from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import requests
import json

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


#APIs

@csrf_exempt
def getNews(request):
    try:
        response = {}
        data = json.loads(request.body)
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/list"
        params = {
            "region": "IN",
            "snippetCount": 4,
            "s": data["symbol"]
        }
        headers = {
            "X-RapidAPI-Key": "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710",
            "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
        results = requests.request("POST", url, headers=headers, params=params).json()
        response["results"] = results
    except Exception as e:
        response["status"] = "failed"
        response["message"] = "Error: " + str(e)
    else:
        response["status"] = "status"
    finally:
        return JsonResponse(response, safe=False)
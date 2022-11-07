from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from .models import Stock, StockNews
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
def searchStock(request):
    try:
        response = []
        data = json.loads(request.body)
        q = data["q"]
        db_results = Stock.objects.filter(
            Q(symbol__icontains = q) | 
            Q(full_name__icontains = q)
        )
        if db_results:
            for result in db_results:
                data = {
                    "name": result.full_name,
                    "symbol": result.symbol,
                    "currency": result.currency
                }
                response.append(data)
        else:
            url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/auto-complete"
            params = {
                "q": data["q"]
            }
            headers = {
                "X-RapidAPI-Key": "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710",
                "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
            }
            api_response = requests.request("GET", url, headers=headers, params=params).json()
            api_results = api_response["quotes"]
            for result in api_results:
                if result["exchDisp"] == "NSE" and "longname" in result.keys():
                    stock = Stock.objects.create(
                        symbol = result["symbol"],
                        full_name = result["longname"],
                        currency = "INR"
                    )
                    data = {
                        "name": result["longname"],
                        "symbol": result["symbol"],
                        "currency": "INR"
                    }
                    response.append(data)
    except Exception as err:
        print("Error: ", err)
    finally:
        return JsonResponse(response, safe=False)

@csrf_exempt
def getNews(request):
    try:
        response = {}
        data = json.loads(request.body)
        # url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/list"
        # params = {
        #     "region": "IN",
        #     "snippetCount": 4,
        #     "s": data["symbol"]
        # }
        # headers = {
        #     "X-RapidAPI-Key": "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710",
        #     "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
        # }
        # results = requests.request("POST", url, headers=headers, params=params).json()
        stock = Stock.objects.get(symbol=data["symbol"])
        news = StockNews.objects.filter(stock=stock)
        results = []
        for row in news:
            news_item = {
                "id": row.news_id,
                "title": row.title,
                "publish_date": row.publish_date,
                "thumbnail": row.thumbnail
            }
            results.append(news_item)
        response["results"] = results
    except Exception as e:
        response["status"] = "failed"
        response["message"] = "Error: " + str(e)
    else:
        response["status"] = "status"
    finally:
        return JsonResponse(response, safe=False)
from .models import Stock, StockNews, VisitedStock
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
import requests
import logging
import json

logger = logging.getLogger("debug")

def getNewsFromApi(symbol):
    try:
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/list"
        params = {
            "region": "IN",
            "snippetCount": 4,
            "s": symbol
        }
        headers = {
            "X-RapidAPI-Key": "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710",
            "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
        results = requests.request("POST", url, headers=headers, params=params).json()
    except Exception as e:
        logger.error(str(e))
        return False
    else:
        return results


def saveNewsInDb():
    try:
        logger.warning("running by crontab at " + str(timezone.now()))
        stocks = VisitedStock.objects.all()
        for visited_stock in stocks:
            stock = Stock.objects.get(stock = visited_stock)
            api_results = getNewsFromApi(stock.symbol)
            if not api_results:
                return False
            for news_item in api_results:
                news_content = news_item["content"]
                id = news_content["id"]
                title = news_content["title"]
                pub_date = news_content["pubDate"]
                thumbnail = news_content["thumbnail"]["resolutions"][0]["url"]
                StockNews.objects.create(
                    news_id = id,
                    stock = stock,
                    title = title,
                    publish_date = pub_date,
                    thumbnail = thumbnail
                )
    except IntegrityError:
        logger.info("News Alredy Exists do nothing: " + title)
    except Exception as e:
        logger.error(str(e))

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
        stock = Stock.objects.get(symbol=data["symbol"])
        visited_stock = VisitedStock.objects.filter(stock=stock)

        if not visited_stock:
            visited_stock = VisitedStock.objects.create(
                stock = stock,
                unique_visited = 1
            )
            if request.user.is_authenticated:
                visited_stock.visited_by.add(request.user)
        else:
            if request.user.is_authenticated:
                if not visited_stock[0].visited_by.contains(request.user):
                    visited_stock[0].unique_visited += 1
                    visited_stock[0].save()

        news = StockNews.objects.filter(
            Q(stock = stock) &
            Q(add_date = timezone.now())
        )
        results = []
        if news:
            logger.warning(f"New find for today for {stock.symbol}")
            for row in news:
                news_item = {
                    "id": row.news_id,
                    "title": row.title,
                    "publish_date": row.publish_date,
                    "thumbnail": row.thumbnail
                }
                results.append(news_item)
        else:
            logger.warning(f"News are not present for {stock.symbol}! fetching from API")
            api_results = getNewsFromApi(data["symbol"])
            if not api_results:
                raise Exception
            news = api_results["data"]["main"]["stream"]
            for news_item in news:
                news_content = news_item["content"]
                id = news_content["id"]
                title = news_content["title"]
                pub_date = news_content["pubDate"]
                thumbnail = news_content["thumbnail"]["resolutions"][0]["url"]

                StockNews.objects.create(
                    news_id = id,
                    stock = stock,
                    title = title,
                    publish_date = pub_date,
                    thumbnail = thumbnail
                ).save()
                result = {
                    "id": id,
                    "title": title,
                    "publish_date": pub_date,
                    "thumbnail": thumbnail
                }
                results.append(result)
        response["results"] = results
    except Exception as e:
        response["status"] = "failed"
        response["message"] = "Error: " + str(e)
        logger.error(str(e))
    else:
        response["status"] = "status"
    finally:
        return JsonResponse(response, safe=False)
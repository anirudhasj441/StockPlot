from django.views.decorators.csrf import csrf_exempt
from .models import Stock, StockNews, VisitedStock
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.text import Truncator
from django.http import JsonResponse, HttpResponse
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
            stock = Stock.objects.get(symbol = visited_stock)
            api_results = getNewsFromApi(stock.symbol)
            if not api_results:
                return False
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
                )
    except IntegrityError:
        logger.warning("News Alredy Exists do nothing: " + title)
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

def newsContent(request, id):
    try:
        news = StockNews.objects.get(news_id=id)
        news_content = news.content
        if not news_content:
            logger.warning("Fetching content from api!")
            url = "https://yh-finance.p.rapidapi.com/news/v2/get-details"
            querystring = {
                "uuid": id,
                "region": "IN"
            }
            headers = {
                "X-RapidAPI-Key": "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710",
                "X-RapidAPI-Host": "yh-finance.p.rapidapi.com"
            }
            response = requests.request("GET", url, headers=headers, params=querystring).json()
            news_content = response["data"]["contents"][0]["content"]["body"]["markup"]
            news.content = news_content
            news.save()
        else:
            logger.warning("Fetchin content from database!!!")
    except StockNews.DoesNotExist:
        return HttpResponse("<h1>Invalid News Id</h1>")
    else:
        return HttpResponse(news_content)

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
                    "title": Truncator(row.title).chars(50),
                    "publish_date": naturaltime(row.publish_date),
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
                
                previous_news = StockNews.objects.filter(news_id = id)
                if previous_news:
                    logger.warning(f"Existing news found for {stock.symbol} changing add date: {str(timezone.now())}")
                    previous_news_obj = previous_news[0]
                    previous_news_obj.add_date = timezone.now()
                    previous_news_obj.save()
                    result = {
                        "id": previous_news_obj.news_id,
                        "title": previous_news_obj.title,
                        "publish_date": naturaltime(previous_news_obj.publish_date),
                        "thumbnail": previous_news_obj.thumbnail
                    }
                else:
                    StockNews.objects.create(
                        news_id = id,
                        stock = stock,
                        title = title,
                        publish_date = pub_date,
                        thumbnail = thumbnail
                    )
                    result = {
                        "id": id,
                        "title": title,
                        "publish_date": naturaltime(pub_date),
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
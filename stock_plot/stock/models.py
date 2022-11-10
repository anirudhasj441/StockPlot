from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Stock(models.Model):
    symbol = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=100)
    last_check = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.symbol)

class StockNews(models.Model):
    news_id = models.CharField(max_length=500, unique=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=True, blank=True)
    publish_date = models.DateTimeField()
    thumbnail = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    add_date = models.DateField(default=timezone.now)
    def __str__(self):
        return str(self.news_id)

class StockTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    upper_limit = models.FloatField(null=True, blank=True)
    lower_limit = models.FloatField(null=True, blank=True)
    def __str__(self):
        return str(self.pk)

class VisitedStock(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    visited_by = models.ManyToManyField(User, blank=True)
    unique_visited = models.IntegerField(null=True, blank=True, default=0)
    def __str__(self):
        return str(self.stock.symbol)
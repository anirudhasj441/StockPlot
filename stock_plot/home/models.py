from django.db import models
from django.contrib.auth.models import User
from stock.models import Stock

# Create your models here.

class StockWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stocks = models.ManyToManyField(Stock)
    def __str__(self):
        return str(self.user.username)
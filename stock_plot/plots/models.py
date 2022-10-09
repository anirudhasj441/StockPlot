from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Stock(models.Model):
    symbol = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    price = models.FloatField()
    currency = models.CharField(max_length=100)
    last_check = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.symbol)

class StockTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    upper_limit = models.FloatField(null=True, blank=True)
    lower_limit = models.FloatField(null=True, blank=True)
    def __str__(self):
        return str(self.pk)
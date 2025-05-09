from django.contrib.auth.models import User
from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    price = models.FloatField()
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.symbol} - {self.date}"

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    close_price = models.FloatField()
    sma20 = models.FloatField(null=True, blank=True)
    sma50 = models.FloatField(null=True, blank=True)
    macd = models.FloatField(null=True, blank=True)
    signal = models.FloatField(null=True, blank=True)
    rsi = models.FloatField(null=True, blank=True)

def __str__(self):
        return f"{self.symbol} - {self.date}"
    
class CandlestickPattern(models.Model):
    name = models.CharField(max_length=100)
    signal = models.CharField(max_length=255)
    details_url = models.URLField()

    def __str__(self):
        return self.name
    


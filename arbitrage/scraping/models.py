from django.db import models

# Create your models here.

class Result(models.Model):
    username = models.CharField(max_length=64)
    source_product = models.CharField(max_length=64)
    target_price = models.DecimalField(max_digits=32, decimal_places=8)
    product = models.CharField(max_length=64)
    retailer = models.CharField(max_length=64)
    url = models.CharField(max_length=512)
    retailer_price = models.DecimalField(max_digits=32, decimal_places=8)
    date = models.DateTimeField()
    asin = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id}: {self.username}.\nProduct {self.product[:20]} for {self.source_product[:20]}.\nTarget price: {self.target_price}. Price: {self.retailer_price}"

class User(models.Model):
    username = models.CharField(max_length=64)
    API_KEY = models.CharField(max_length=64)
    requests = models.IntegerField()
    flagged_requests = models.IntegerField()
    to_be_billed = models.DecimalField(max_digits=32, decimal_places=8)

    def __str__(self):
        return f"{self.username}"

class Blacklist(models.Model):
    username = models.CharField(max_length=64)
    url = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.username}: {self.url}"
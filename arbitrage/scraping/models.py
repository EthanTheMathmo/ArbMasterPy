from django.db import models

# Create your models here.

class Result(models.Model):
    username = models.CharField(max_length=64)
    source_product = models.CharField(max_length=64)
    product = models.CharField(max_length=64)
    retailer = models.CharField(max_length=64)
    url = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=32, decimal_places=8)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.id}: {self.username}. Product {self.product} for {self.source_product} at {self.price}"

class User(models.Model):
    username = models.CharField(max_length=64)
    API_KEY = models.CharField(max_length=64)
    requests = models.IntegerField()
    flagged_requests = models.IntegerField()
    to_be_billed = models.DecimalField(max_digits=32, decimal_places=8)

    def __str__(self):
        return f"{self.username}"
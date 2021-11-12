from django.db import models

# Create your models here.

class results(models.Model):
    user = models.CharField(max_length=64)
    source_product = models.CharField(max_length=64)
    product = models.CharField(max_length=64)
    retailer = models.CharField(max_length=64)
    url = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=32, decimal_places=8)
    date = models.DateTimeField()
    name = models.CharField(max_length=64)

from django.db import models



# Create your models here.
class User_search_count(models.Model):
    username = models.CharField(max_length=64)
    date = models.DateTimeField()
    number_searches_run = models.IntegerField() #actual number of searches made using the search APIs
    number_of_searches_completed = models.IntegerField() #number of searches which sucessfully completed
    number_of_results = models.IntegerField() #number of results which remained after filters

    def __str__(self):
        return f"""{self.id}: {self.username}. Date: {self.date}. 
        Number searches run: {self.number_searches_run}
        number searches completed: {self.number_of_searches_completed}
        number of results: {self.number_of_results}"""

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
    result_id = models.IntegerField()
    web_address = models.CharField(max_length=512)

    def __str__(self):
        return f"""{self.id}: {self.username}.\nProduct {self.product[:20]} for {self.source_product[:20]}.\nTarget price: {self.target_price}. Price: {self.retailer_price}
        result id: {self.result_id}"""

class User(models.Model):
    username = models.CharField(max_length=64)
    API_KEY = models.CharField(max_length=64)
    requests = models.IntegerField() #
    flagged_requests = models.IntegerField()
    to_be_billed = models.DecimalField(max_digits=32, decimal_places=8)
    file_upload_count = models.IntegerField(default=0) # to keep track of number of files uploaded
                                                #when we add a new file, we use this value to index
                                                #its values in Result database, and increment it by 1
    def __str__(self):
        return f"""Username: {self.username}, API_KEY <>, requests: {self.requests}, flagged_requests: {self.flagged_requests}
        to be billed: {self.to_be_billed}"""

class Blacklist(models.Model):
    username = models.CharField(max_length=64)
    url = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.username}: {self.url}"
from django.db import models


class ProductSearchModel(models.Model):

    query = models.CharField(max_length=50)
    number = models.IntegerField(default=5)


class ProductModel(models.Model):

    url = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    price_date = models.DateTimeField()
    img_url = models.CharField(max_length=300)
    search = models.ForeignKey(to=ProductSearchModel, on_delete=models.CASCADE)
    previous_prices = models.CharField(max_length=500000)

from django.db import models
from lugati.lugati_points_of_sale.models import SalesPoint
from lugati.products.models import Product

class PriceList(models.Model):
    point_of_sale = models.ForeignKey(SalesPoint, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)

class PriceListItem(models.Model):
    price_list = models.ForeignKey(PriceList)
    product = models.ForeignKey(Product)
    price = models.FloatField(default=0)
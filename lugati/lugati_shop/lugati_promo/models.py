from django.db import models
from lugati.products.models import Product

class SpecialOffer(models.Model):
    product = models.ForeignKey(Product, primary_key=True)
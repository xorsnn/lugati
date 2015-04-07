from django.db import models
from django.contrib.sites.models import get_current_site
from django.contrib.sites.models import Site

class CoinbaseCallback(models.Model):
    callback_body = models.TextField()

class CallbackTickets(models.Model):
    cart_id = models.CharField(max_length=100)
    site = models.ForeignKey(Site)


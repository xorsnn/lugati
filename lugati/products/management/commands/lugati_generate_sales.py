# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError
import sys
from random import randint

import logging
from django.contrib.contenttypes.models import ContentType
from lugati.products.models import Product, ProductPrice, Brand
import json
from django.core.files import File
from django.contrib.sites.models import Site
import psycopg2
from lugati.lugati_media.models import ThebloqImage
import requests
#from urllib.parse import urljoin
try:  # Python 3
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import lxml
from lxml.html import fromstring
from BeautifulSoup import BeautifulSoup
import cStringIO
import urllib2
import json
import urllib
from lxml import html
from lxml import etree
from PIL import Image
logger = logging.getLogger(__name__)
from django.conf import settings
import os
from urlparse import urlparse
from django.core.files.uploadedfile import InMemoryUploadedFile
import StringIO
from lugati.lugati_registration.models import LugatiUserProfile
import datetime
from lugati.lugati_shop.lugati_orders.models import Order, OrderItem
from lugati.lugati_shop.models import ShoppingPlace, Shop

from django.db import connection
import random
BASE_FB_ALBUM_NAME='Thebloq'

CUR_SITE = 6

HISTORY_LENGTH = 7

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):

        Order.objects.filter(site=Site.objects.get(pk=CUR_SITE)).delete()







            # date = models.DateTimeField(auto_now_add=True)
            # paid = models.BooleanField(default=False)
            # delivered = models.BooleanField(default=False)
            # cart_id = models.CharField(max_length=50,  blank=True, null=True)
            # site = models.ForeignKey(Site)
            # state = models.ForeignKey(OrderState, default=get_default_state)
            # dt_modify = models.DateTimeField(auto_now=True)
            # dt_add = models.DateTimeField(auto_now_add=True, editable=False)
            #
            # delivery_price = models.DecimalField(default=0, max_digits=15, decimal_places=8)
            # shopping_place = models.ForeignKey(ShoppingPlace, blank=True, null=True)
            #
            # #additional client fields
            # email = models.EmailField(null=True, blank=True)
            # phone = models.CharField(max_length=200, null=True, blank=True)
            # address = models.TextField(null=True, blank=True)
            # delivery_option = models.ForeignKey(DeliveryOption, null=True, blank=True)
            # city = models.CharField(max_length=200, null=True, blank=True)
            # zip_code = models.CharField(max_length=200, null=True, blank=True)
            # name = models.CharField(max_length=200, null=True, blank=True)
            # tracking_number = models.CharField(max_length=200, null=True, blank=True)
            #
            # receipt_path = models.CharField(max_length=500, blank=True, null=True)



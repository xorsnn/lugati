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

import urllib2
import json
import urllib
from lxml import html
from lxml import etree

logger = logging.getLogger(__name__)
from django.conf import settings
import os
from urlparse import urlparse
from lugati.lugati_widgets.models import LugatiTextBlock, LugatiNews, LugatiPoem
from lugati.lugati_shop.lugati_orders.models import Order
from lugati.lugati_shop.lugati_delivery.models import DeliveryOption

BASE_FB_ALBUM_NAME='Thebloq'

CUR_SITE = 3

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):
        # logger.info('start export products: ' + str(datetime.datetime.now()))

        site = Site.objects.get(pk=CUR_SITE)
        str = self.to_json(site)
        str = json.dumps(str)
        file = open('sola_export.json', 'w')
        file.write(str)
        file.close()

    def to_json(self, site):

        res = {
            'products': self.get_products_json(site),
            'text_blocks': self.get_text_blocks_json(site),
            'poems': self.get_poems_json(site),
            'photo': self.get_photo_json(site),
            'video': self.get_video_json(site),
            'orders': self.get_orders_json(site),
            'delivery_options': self.get_delivery_options_json(site)
        }
        return res

    def get_delivery_options_json(self, site):
        print 'exporting delivery options'
        nodes = []
        objects = DeliveryOption.objects.filter(site=site)
        for object in objects:
            node = object.get_list_item_info(export=True)
            nodes.append(node)
        return nodes

    def get_text_blocks_json(self, site):
        print 'exporting text blocks'
        nodes = []
        objects = LugatiTextBlock.objects.filter(site=site)
        for object in objects:
            node = object.get_list_item_info(export=True)
            nodes.append(node)
        return nodes

    def get_poems_json(self, site):
        print 'exporting poems'
        nodes = []
        objects = LugatiPoem.objects.filter(site=site)
        for object in objects:
            node = object.get_list_item_info(export=True)
            nodes.append(node)
        return nodes

    def get_photo_json(self, site):
        print 'exporting photo'
        return []

    def get_video_json(self, site):
        print 'exporting video'
        return []

    def get_orders_json(self, site):
        print 'exporting orders'
        nodes = []
        objects = Order.objects.filter(site=site)
        for object in objects:
            node = object.get_list_item_info(export=True)
            nodes.append(node)
        return nodes

    def get_products_json(self, site):
        print 'exporting products'
        res = {}
        def rec_get(parent_object):
            nodes = []
            prods = Product.objects.filter(parent_object=parent_object).filter(site=site)
            for prod in prods:
                node = {
                    'code': prod.code,
                    'sku': prod.sku,
                    'name': prod.name,
                    'description': prod.description,
                    'preview': prod.preview,
                    'is_category': prod.is_category,
                    'active': prod.active,
                    'priority': prod.priority,
                    'site': prod.site.id,
                    'additional_info': prod.additional_info,
                    'in_stock': prod.in_stock,
                    'price_wo_discount': str(prod.price_wo_discount),
                    'price': str(prod.price),

                  # 'brand': prod.brand.id,
                  #   'company': prod.company.id,
                    #'main_image': prod.main_image,
                    'children': rec_get(prod),
                    'images': []
                }
                if prod.company:
                    node['company'] = prod.company.id
                for img in prod.get_images():
                    node['images'].append(img.to_string())
                nodes.append(node)
            return nodes
        res = rec_get(None)
        return res

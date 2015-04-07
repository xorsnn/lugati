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
from lugati.lugati_widgets.models import LugatiTextBlock, LugatiNews, LugatiPoem
from lugati.lugati_shop.lugati_orders.models import Order
from lugati.lugati_shop.lugati_delivery.models import DeliveryOption, City
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_shop.lugati_orders.models import Order

BASE_FB_ALBUM_NAME='Thebloq'

CUR_SITE = 3

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):
        file = open('sola_export.json', 'r')
        str = file.read()
        res = json.loads(str)

        clear_items = True
        site = Site.objects.get(pk=CUR_SITE)

        if clear_items:
            Product.objects.filter(site=site).delete()
        self.load_products(site=site, products=res['products'], clear_items=clear_items)

        if clear_items:
            DeliveryOption.objects.filter(site=site).delete()
        self.load_delivery_options(site=site, delivery_options=res['delivery_options'], clear_items=clear_items)

        # todo!!!!
        # 'text_blocks': self.get_text_blocks_json(site),
        # 'poems': self.get_poems_json(site),
        # 'photo': self.get_photo_json(site),
        # 'video': self.get_video_json(site),
        # 'orders': self.get_orders_json(site),

        # from lugati.products.products_procs import load_demo_data, generate_week_sales, create_demo_account
        # create_demo_account(CUR_SITE, User.objects.get(username='sgrigorev'))

    def load_delivery_options(self, site, delivery_options, clear_items=False):
        print 'loading delivery options'

        for delivery_option in delivery_options:
            new_opt = DeliveryOption()
            new_opt.name = delivery_option['name']
            new_opt.price = float(delivery_option['price'])
            new_opt.additional_price = float(delivery_option['additional_price'])
            new_opt.site = site
            new_opt.online_payment = delivery_option['online_payment']
            new_opt.active = delivery_option['active']
            new_opt.del_opt = delivery_option['del_opt']
            new_opt.mail_text = delivery_option['mail_text']
            new_opt.city = self.load_city(site, delivery_option['city'])
            new_opt.save()

    def load_city(self, site, city):
        print 'loading city: ' + city['name']
        try:
            new_city = City.objects.get(comment=city['comment'])
        except:
            new_city = City()
            new_city.is_region = city['is_region']
            new_city.name = city['name']
            new_city.priority = city['priority']
            new_city.comment = city['comment']
            new_city.lng = city['lng']
            new_city.lat = city['lat']
            new_city.site = site

            if 'region' in city:
                new_city.region = self.load_city(site, city['region'])

            new_city.save()

        return  new_city

    def load_products(self, site, products, clear_items=False):

        def rec_proc(ms, parent=None):
            for prod in ms:
                new_prod = Product()
                new_prod.code = prod['code']
                new_prod.sku = prod['sku']
                new_prod.name = prod['name']
                new_prod.description = prod['description']
                new_prod.preview = prod['preview']
                new_prod.is_category = prod['is_category']
                new_prod.active = prod['active']
                new_prod.priority = prod['priority']
                # ????
                new_prod.site = site
                new_prod.additional_info = prod['additional_info']
                new_prod.in_stock = prod['in_stock']
                new_prod.price_wo_discount = float(prod['price_wo_discount'])
                new_prod.price = float(prod['price'])
                new_prod.parent_object = parent

                #to company??
                # new_prod.company = LugatiUserProfile.objects.get(user=user).get_company()

                new_prod.save()
                for img in prod['images']:
                    file_like = cStringIO.StringIO(img.decode('base64'))
                    img = Image.open(file_like)

                    tempfile_io = StringIO.StringIO()
                    img.save(tempfile_io, format='PNG')

                    tb_image = ThebloqImage()
                    tb_image.file = InMemoryUploadedFile(tempfile_io, None, 'prod_img.png', 'image/png', tempfile_io.len, None)
                    tb_image.content_object = new_prod
                    tb_image.save()

                print prod['name']
                rec_proc(prod['children'], new_prod)
        rec_proc(products)




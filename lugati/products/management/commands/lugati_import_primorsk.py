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

BASE_FB_ALBUM_NAME='Thebloq'

CUR_SITE = 10

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):
        logger.info('start import products: ' + str(datetime.datetime.now()))
        self.recompose_creations()

    def format_str(self, arg, delimiter=' '):
        res = ''
        for s in arg:
            res += (s + delimiter)
        return res.strip()

    def create_product(self, name, img_srcs, preview, description, cat, brand=None, item_link='', price = 0):
        product = Product()
        product.name = name
        product.preview = preview
        product.site = Site.objects.get(pk=CUR_SITE)
        product.parent_object = cat
        product.brand = brand
        product.description = description
        product.additional_info = item_link.strip()
        product.save()

        product.set_price(price)

        for img_src in img_srcs:
            tb_image = ThebloqImage()

            file_save_dir = 'static/upload'
            filename = urlparse(img_src).path.split('/')[-1]

            r = requests.get(img_src)
            with open(os.path.join(file_save_dir, filename),'wb') as f:
                f.write(r.content)

            tb_image.file = File(open(os.path.join(file_save_dir, filename)))
            tb_image.content_object = product
            tb_image.save()

    def get_description_price(self, base_link, product_link):
        r = requests.get(base_link+product_link)
        doc = html.fromstring(r.text)
        #desc = self.format_str(arg=doc.xpath('//*[@id="main"]/div/div[1]/div[2]/p/text()'), delimiter='\n')
        desc = etree.tostring(doc.xpath('//*[@id="main"]/div/div[1]/div[2]')[0], pretty_print=True)
        price = float(doc.xpath('//*[@id="main"]/div/div[1]/div[1]/div/p[1]/ins/strong/text()')[0])
        return desc, price

    def create_products(self, base_link, category_link, cat, brand):
        r = requests.get(base_link+category_link)
        doc = html.fromstring(r.text)
        items = doc.xpath('//*[@id="leaders"]/div')

        for item in items:

            name = self.format_str(item.xpath('div/p/a/text()'))
            item_link = item.xpath('div/p/a')[0].attrib['href']

            img_srcs = []
            img_src = base_link+(item.xpath('div/p[2]/span/img')[0].attrib['src']).replace('/resources/catalog/small','/resources/catalog').strip()
            img_srcs.append(img_src)

            preview = self.format_str(item.xpath('div/p[3]/text()'))
            description, price = self.get_description_price(base_link, item_link)

            self.create_product(name=name, img_srcs=img_srcs, preview=preview, description=description, cat=cat, brand=brand, item_link=item_link, price=price)

    def get_brand_pages(self, base_link, brand_link, cat, brand):

        r = requests.get(base_link + brand_link)
        doc = html.fromstring(r.text)
        pages = doc.xpath('//*[@id="pager"]/p/a')

        self.create_products(base_link=base_link, category_link=brand_link, cat=cat, brand=brand)
        for page in pages:
            self.create_products(base_link=base_link, category_link=page.attrib['href'], cat=cat, brand=brand)



    def get_brands(self, base_link, category_link, cat):
        r = requests.get(base_link+category_link)
        doc = html.fromstring(r.text)
        items = doc.xpath('//*[@id="vendors"]/p/span')

        for item in items:
            brand_name = item.text

            brand = None
            try:
                brand = Brand.objects.get(name=brand_name)
            except:
                brand = Brand()
                brand.name = brand_name
                brand.site = Site.objects.get(pk=CUR_SITE)
                brand.save()

            brand_link = item.attrib['rel']
            self.get_brand_pages(base_link=base_link, brand_link=brand_link, cat=cat, brand=brand)

    def get_links(self, base_link):

        r = requests.get(base_link)
        doc = html.fromstring(r.text)

        rows = doc.xpath('//*[@id="categories"]/div/div/ul')[0].findall('li')
        for row in rows:
            href = row.xpath('span/a')[0].get('href')
            text = self.format_str(row.xpath('span/a/span/text()'))

            category = Product()
            category.name = text
            category.site = Site.objects.get(pk=CUR_SITE)
            category.is_category = True
            category.save()

            print href
            if row.xpath('span/div/div/ul'):
                sub_rows = row.xpath('span/div/div/ul')[0].findall('li')
                for sub_row in sub_rows:
                    href = sub_row.xpath('span/a')[0].get('href')
                    text = self.format_str(sub_row.xpath('span/a/span/text()'))

                    sub_category = Product()
                    sub_category.name = text
                    sub_category.is_category = True
                    sub_category.site = Site.objects.get(pk=CUR_SITE)
                    sub_category.parent_object = category
                    sub_category.save()

                    self.get_brands(base_link, href, sub_category)



    def recompose_creations(self):
        logger.info('deleting')
        products = Product.objects.filter(site=None)
        for product in products:
            product.get_images().delete()
            product.get_prices().delete()
        products.delete()
        products = Product.objects.filter(site=Site.objects.get(pk=CUR_SITE))
        for product in products:
            product.get_images().delete()
            product.get_prices().delete()
        products.delete()
        Brand.objects.filter(site=Site.objects.get(pk=CUR_SITE)).delete()


        self.get_links('http://1bt.spb.ru/')


        #        if (str(unicode(row[2])) == '8') and (str(unicode(row[3])) <> 'None') and (imgs[str(row[0])]['object_id'] in products.keys()):
        #            logger.info('aaa')
        #            tb_image = ThebloqImage()
        #            #tb_image.file = File(open('/var/www/artel-grigorieva.ru/static/'+row[1]))
        #            tb_image.file = File(open('/var/www/atecar.ru/static/'+row[1]))
        #            logger.info(str(products[str(unicode(row[3]))]))
        #            tb_image.content_object = products[str(unicode(row[3]))]['object']
        #            tb_image.save()
        #
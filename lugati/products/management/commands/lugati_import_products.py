# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError
import sys
from random import randint

import logging
from django.contrib.contenttypes.models import ContentType
from lugati.products.models import Product, ProductPrice
import json
from django.core.files import File
from django.contrib.sites.models import Site
import psycopg2
from lugati.lugati_media.models import ThebloqImage
logger = logging.getLogger(__name__)
from django.conf import settings

BASE_FB_ALBUM_NAME='Thebloq'

CUR_SITE = 2

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):
        logger.info('start import products: ' + str(datetime.datetime.now()))
        self.recompose_creations()

    def recompose_creations(self):
        logger.info('deleting')
        products = Product.objects.filter(site=Site.objects.get(pk=CUR_SITE))
        for product in products:
            product.get_images().delete()
            product.get_prices().delete()
        products.delete()


        #conn = psycopg2.connect(host="127.0.0.1", dbname="artel-grigorieva", user="artel-grigorieva", password="artel-grigorieva")
        conn = psycopg2.connect(host="127.0.0.1", dbname="atecar", user="atecar", password="atecar")
        cur = conn.cursor()
        #cur.execute('select id, name, description, parent_product_id, is_category, preview, priority from products_product order by is_category desc, parent_product_id desc')
        cur.execute('select id, name, description, parent_product_id, is_category, preview, 1, sku from products_product order by is_category desc, parent_product_id desc')
        rows = cur.fetchall()
        products = {}
        for row in rows:
            logger.info(row[4])
            if row[7]:
                products[str(row[0])] = {
                    'name': unicode(row[1]),
                    'description': unicode(row[2]),
                    'parent_product_id': str(row[3]),
                    'is_category': str(row[4]),
                    'preview': unicode(row[5]),
                    'priority': str(row[6]),
                    'sku': unicode(row[7]),
                    'object': None
                }
            else:
                products[str(row[0])] = {
                    'name': unicode(row[1]),
                    'description': unicode(row[2]),
                    'parent_product_id': str(row[3]),
                    'is_category': str(row[4]),
                    'preview': unicode(row[5]),
                    'priority': str(row[6]),
                    'sku': '',
                    'object': None
                }

        for prod_key in products.keys():
            prod = Product()
            #prod.site = Site.objects.get(pk=1)
            prod.site = Site.objects.get(pk=CUR_SITE)
            prod.name = products[prod_key]['name']
            prod.description = products[prod_key]['description']
            if str(products[prod_key]['is_category']) == 'True':
                prod.is_category = True
            else:
                prod.is_category = False
            prod.preview = products[prod_key]['preview']
            prod.priority = products[prod_key]['priority']
            prod.sku = products[prod_key]['sku']
            #if products[prod_key]['parent_product_id'] <> 'None':
            #    prod.parent_product = products[products[prod_key]['parent_product_id']]['object']
            prod.save()
            products[prod_key]['object'] = prod
        for prod_key in products.keys():
            if str(products[prod_key]['parent_product_id']) <> 'None':
                products[prod_key]['object'].parent_product = products[products[prod_key]['parent_product_id']]['object']
            products[prod_key]['object'].save()


        try:
            cur.execute('select id, original_image, content_type_id, object_id  from images_image')
            #ThebloqImage.objects.all().delete()
            rows = cur.fetchall()
            imgs = {}
            for row in rows:
                logger.info(row[2])
                imgs[str(row[0])] = {
                    'original_image': unicode(row[1]),
                    'content_type_id': unicode(row[2]),
                    'object_id': str(row[3])
                }
                #if (str(unicode(row[2])) == '12') and (str(unicode(row[3])) <> 'None') and (imgs[str(row[0])]['object_id'] in products.keys()):
                if (str(unicode(row[2])) == '8') and (str(unicode(row[3])) <> 'None') and (imgs[str(row[0])]['object_id'] in products.keys()):
                    logger.info('aaa')
                    tb_image = ThebloqImage()
                    #tb_image.file = File(open('/var/www/artel-grigorieva.ru/static/'+row[1]))
                    tb_image.file = File(open('/var/www/atecar.ru/static/'+row[1]))
                    logger.info(str(products[str(unicode(row[3]))]))
                    tb_image.content_object = products[str(unicode(row[3]))]['object']
                    tb_image.save()
        except Exception, e:
            logger.info(str(e))

        cur.execute('select id, product_id, price, dt_modify, dt_add from products_productprice')
        rows = cur.fetchall()
        #ProductPrice.objects.all().delete()
        prs = {}
        for row in rows:
            prs[str(row[0])] = {
                'prooduct_id': unicode(row[1]),
                'price': float(row[2]),
                'dt_modify': unicode(row[3]),
                'dt_add': unicode(row[4])
            }
            if str(row[1]) in products.keys():
                prod_price = ProductPrice()
                prod_price.product = products[str(row[1])]['object']
                prod_price.price = float(row[2])
                prod_price.dt_modify = unicode(row[3])
                prod_price.dt_add = unicode(row[4])
                prod_price.save()

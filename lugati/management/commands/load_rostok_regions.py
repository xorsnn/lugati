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
from lugati.lugati_points_of_sale.models import City
BASE_FB_ALBUM_NAME='Thebloq'

CUR_SITE = 8

DOMAIN = 'http://bioice.ru/wheretobuy/'

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):
        logger.info('start import products: ' + str(datetime.datetime.now()))
        self.recompose_creations()

    def get_links(self, base_link):

        r = requests.get(base_link)
        doc = html.fromstring(r.text)

        region = None
        town = None

        cats = doc.xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div[1]/div')
        for cat in cats:
            if 'class' in cat.attrib:
                if ('region-name' in cat.attrib['class']) and ('j_region_name' in cat.attrib['class']):
                    name = cat.xpath('span')[0].text
                    region = City()
                    region.name = name
                    region.site = Site.objects.get(pk=CUR_SITE)
                    region.is_category = True
                    region.save()
                    pass
                elif ('town-list' in cat.attrib['class']) and ('j_town_list' in cat.attrib['class']):
                    for link in cat.xpath('a'):
                        if 'class' in link.attrib:
                            if 'town j_region' in link.attrib['class']:
                                name = link.text
                                if region:
                                    town = City()
                                    town.name = name
                                    town.site = Site.objects.get(pk=CUR_SITE)
                                    town.parent_object = region
                                    town.save()
                                pass

    def recompose_creations(self):
        # print 1
        City.objects.filter(site=Site.objects.get(pk=CUR_SITE)).delete()
        self.get_links(DOMAIN)



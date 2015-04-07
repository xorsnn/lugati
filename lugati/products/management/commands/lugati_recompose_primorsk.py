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
from random import randint
BASE_FB_ALBUM_NAME='Thebloq'

from django.contrib.sites.models import Site

CUR_SITE = 5

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):
        logger.info('start import products: ' + str(datetime.datetime.now()))
        self.recompose_creations()

    def recompose_creations(self):
        logger.info('recomposing')

        categories = Product.objects.filter(site=Site.objects.get(pk=CUR_SITE)).filter(is_category=True)
        for category in categories:
            imgs = category.get_images()
            if imgs.count() == 0:
                children = Product.objects.filter(parent_product=category)
                if children.count() > 0:
                    ind = randint(0, children.count()-1)
                    imgs_to_assign = children[ind].get_images()
                    for img in imgs_to_assign:

                        tb_image = ThebloqImage()
                        tb_image.file = File(open(img.file.file.name))
                        tb_image.content_object = category
                        tb_image.save()
                        logger.info('assigned ' + category.name)


                        break


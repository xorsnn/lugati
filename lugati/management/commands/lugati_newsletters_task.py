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

logger = logging.getLogger(__name__)
from django.conf import settings
import os
from urlparse import urlparse
from lugati.lugati_shop.lugati_orders.models import OrderState
from django.contrib.sites.models import Site
from lugati.lugati_media.lugati_gallery.models import GalleryItem
from lugati.lugati_media.models import ThebloqFont
from lugati.products.models import ProductPrice
from django.contrib.auth.models import User
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_shop.models import Shop, LugatiCompany, LugatiCurrency
import time
from lugati.lugati_feedback.models import LugatiNewsletterTask, LugatiNewsletterSignUp
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template

class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):

        while True:
            logger.info('start newsletter check: ' + str(datetime.datetime.now()))

            tasks = LugatiNewsletterTask.objects.filter(done=False)

            for task in tasks:
                if task.content_type.model_class().__name__ == 'LugatiNews':
                    obj = task.content_type.model_class().objects.get(pk=task.object_id)
                    cur_site = obj.site
                    t = get_template('custom/' + cur_site.name + '/catalog/newsletter_template.html')
                    message_html = t.render(Context({'object':obj}))
                    subject = u'Новости сайта ' + obj.site.name
                    sign_ups = LugatiNewsletterSignUp.objects.filter(site=cur_site)
                    # emails = []
                    for sign_up in sign_ups:
                        # emails.append(sign_up.email)
                        try:
                            msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, [sign_up.email])
                            msg.attach_alternative(message_html, "text/html")
                            msg.send()
                        except Exception, e:
                            logger.info('newsletter check error')
                            pass

                logger.info('task')
                task.done = True
                task.save()
            time.sleep(60)





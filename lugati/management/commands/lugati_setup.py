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
# from urllib.parse import urljoin
try:  # Python 3
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from lugati.lugati_registration.models import LugatiRole

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
from lugati import lugati_procs

BASE_FB_ALBUM_NAME = 'Thebloq'

ORDER_STATES = (
    (1, 'PAID', 'alert alert-warning'),
    (2, 'ACKNOWLEDGED', 'alert alert-info'),
    (3, 'DONE', 'alert alert-success'),
    (4, 'CANCELLED&REFUNDED', 'alert alert-danger')
)

lugati_sites = (
    ('artel-grigorieva.ru', 'artel_grigorieva'),
    ('atecar.ru', 'atecar'),
    ('sola-monova.ru', 'sola-monova'),
    ('lugati.ru', 'lugati_site'),
    ('primorsk.su', 'primorsk'),
    ('mps.com', 'mps'),
    ('lugati-btc.com', 'lugati-btc.com'),
    ('rostokzd.ru', 'rostokzd.ru'),
    ('makemake.us', 'makemake.us'),
    ('geo-term.ru', 'geoterm'),
    ('merchant.lugati.ru', 'mps'),
    ('zuyka.com', 'zuyka'),
    ('идинах.рф', 'fuck_you')
)


class Command(BaseCommand):
    help = 'general procedures'

    def handle(self, *args, **options):
        logger.info('start initial setup: ' + str(datetime.datetime.now()))

        logger.info('sites...')
        ind = 1
        for st in lugati_sites:
            try:
                new_site = Site.objects.get(pk=ind)
            except:
                new_site = Site()
                new_site.id = ind
            new_site.domain = st[0]
            new_site.name = st[1]
            new_site.save()
            ind += 1

        #deleting
        cur_ind = ind-1
        while True:
            cur_site = None
            try:
                cur_site = Site.objects.get(pk=ind)
            except:
                break
            if cur_site:
                cur_site.delete()
            cur_ind += 1

        logger.info('order states...')
        ind = 1
        for state in ORDER_STATES:
            try:
                cur_state = OrderState.objects.get(pk=ind)
            except:
                cur_state = OrderState()
            cur_state.custom_id = state[0]
            cur_state.name = state[1]
            cur_state.class_name = state[2]
            cur_state.save()
            ind += 1

        logger.info('galeries...')
        for site in Site.objects.all():
            if not GalleryItem.objects.filter(site=site).filter(title='default').exists():
                gallery = GalleryItem()
                gallery.title = 'default'
                gallery.site = site
                gallery.save()

        logger.info('profiles...')
        for user in User.objects.all():
            if not LugatiUserProfile.objects.filter(user=user).exists():
                prof = LugatiUserProfile()
                prof.user = user
                prof.save()


        # self.install_fonts()
        logger.info('currencies...')
        currencies = [['RUR', 2, 'fa fa-rub', 'rub'],
                      ['USD', 2, 'fa fa-usd', 'usd'],
                      ['EUR', 2, 'fa fa-eur', 'eur'],
                      ['BTC', 8, 'fa fa-btc', 'usd'],
                      ['THB', 2, 'lugati-thb-icon', 'thb']]

        for currency in currencies:
            try:
                new_cur = LugatiCurrency.objects.get(name=currency[0])
            except:
                new_cur = LugatiCurrency()

            new_cur.name = currency[0]
            new_cur.decimal_fields = currency[1]
            new_cur.icon_class_name = currency[2]
            new_cur.stripe_str = currency[3]
            new_cur.save()

        resp = requests.get('https://www.bitstamp.net/api/ticker/')
        btc_rate = json.loads(resp.text)['last']
        for currency in LugatiCurrency.objects.all():
            currency.btc_rate = float(btc_rate)
            currency.save()
        from lugati.lugati_payment import payment_procs
        payment_procs.update_curreynce_exchange_rates()

        if (User.objects.filter(username='sola_postman').count() == 0):
            user = User.objects.create_user('sola_postman', 'postman@sola-monova.com', 'Ai5eiy7i')
            user.save()
            if (LugatiRole.objects.filter(name='postman').count() == 0):
                role = LugatiRole()
                role.name = 'postman'
                role.save()
            else:
                role = LugatiRole.objects.get(name='postman')
            prof = lugati_procs.get_user_profile(user)
            prof.roles.add(role)


        logger.info('companies...')
        for prof in LugatiUserProfile.objects.all():
            if not prof.company:
                new_company = LugatiCompany()
                new_company.default_currency = LugatiCurrency.objects.get(name='USD')
                new_company.name = 'new company'
                new_company.save()
                prof.company = new_company
                prof.save()

        if (LugatiRole.objects.filter(name='waiter').count() == 0):
            role = LugatiRole()
            role.name = 'waiter'
            role.save()

        self.intall_tooltips()
        self.delete_tooltips_notifications()

        self.init_ordering()


    def init_ordering(self):

        for company in LugatiCompany.objects.all():
            products = Product.objects.filter(company=company)
            priority = 2
            for product in products:
                product.priority = priority
                product.save()
                priority += 1

    def install_fonts(self):
        ThebloqFont.objects.all().delete()
        font_folder = settings.MEDIA_ROOT + 'fonts/'
        for font_file in os.listdir(font_folder):
            logger.info(font_file)
            tb_font = ThebloqFont()

            tb_font.file = File(open(os.path.join(font_folder, font_file)))
            tb_font.save()

    def intall_tooltips(self):
        logger.info('tooltips...')
        from lugati.lugati_admin.models import Tooltip
        # Tooltip.objects.all()
        tooltips = []

        # 1
        # tooltip = "Для наиболее эффективной  работы над формированием  МЕНЮ " \
        #           "рекомендуем  использовать полноценный  компьютер. " \
        #           "Использование планшетов  и смартфонов возможно, " \
        #           "но не  очень удобнов  силу их UI."

        tooltip = "Mycelium Order uses the latest technology and requires a fully updated browser." \
                  "For best results and  smooth user experience we recommend " \
                  "administrating Mycelium Order  using a desktop or laptop " \
                  "computer instead of a mobile devices."

        tooltip_id = 'admin_device_advice'

        tooltips.append({
            'name': tooltip_id,
            'text': tooltip
        })

        # 2 deprecated
        tooltip_id = 'admin_session_length_advice'
        try:
            Tooltip.objects.get(pk=tooltip_id)
        except:
            pass
        # ~

        # 3
        tooltip = "To avoid mixing up subcategories and items " \
                  "and keep the architecture plain and clear, " \
                  "adding subcategories is not possible after an ITEM added."

        tooltip_id = 'menu_mixing_advice'

        tooltips.append({
            'name': tooltip_id,
            'text': tooltip
        })

        for tp in tooltips:
            try:
                print 1
                new_tooltip = Tooltip.objects.get(pk=tp['name'])
            except:
                print 2
                new_tooltip = Tooltip()
                new_tooltip.name = tp['name']
            new_tooltip.text = tp['text']
            new_tooltip.save()

    def delete_tooltips_notifications(self):
        from lugati.lugati_admin.models import TooltipShow
        TooltipShow.objects.all().delete()
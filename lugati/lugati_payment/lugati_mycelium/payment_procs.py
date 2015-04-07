from lugati.lugati_payment.models import BTCPaymentTransaction
from decimal import *
from django.db.models import Count, Min, Sum, Avg
import requests
from lugati.lugati_payment.models import LugatiExchangeRate
import datetime
import time
import json
from hashlib import sha256
import hmac
import requests
from django.conf import settings
import logging
import os
import hashlib
import hmac
import urllib2
import time


def make_request(url, body=None):

    URL = settings.MYCELIUM_API_URL + "/generate_receive_address"
    SECRET = settings.MYCELIUM_SECRET
    API = settings.MYCELIUM_API

    opener = urllib2.build_opener()
    nonce = int(time.time() * 1e6)
    message = str(nonce) + url + ('' if body is None else body)
    signature = hmac.new(SECRET, message, hashlib.sha256).hexdigest()

    headers = {'ACCESS_KEY': API,
               'ACCESS_SIGNATURE': signature,
               'ACCESS_NONCE': nonce,
               'Accept': 'application/json'}

    # If we are passing data, a POST request is made. Note that content_type is specified as json.
    if body:
        headers.update({'Content-Type': 'application/json'})
        req = urllib2.Request(url, data=body, headers=headers)

    # If body is nil, a GET request is made.
    else:
        req = urllib2.Request(url, headers=headers)

    try:
        return opener.open(req)
    except urllib2.HTTPError as e:
        return e

    # dt = datetime.datetime.now()
    # NONCE = int(time.mktime(dt.timetuple())*1000)
    # PAYMENT_CALLBACK_URL = 'http://merchant.mycelium.com/payment/lugati_coinbase/callback/'
    #
    # body = {
    #     'address': {
    #         'callback_url': PAYMENT_CALLBACK_URL + str(1) + '/'
    #     }
    # }
    #
    # BODY = json.dumps(body)
    #
    # TO_SIGN = str(NONCE) + str(URL) + str(BODY)
    #
    # hashed = hmac.new(SECRET, TO_SIGN, sha256)
    #
    # headers = {
    #     'ACCESS_KEY': unicode(API),
    #     'ACCESS_SIGNATURE': unicode(hashed.hexdigest()),
    #     'ACCESS_NONCE': unicode(NONCE),
    #     'Content-Type':  u'application/json'
    # }
    #
    # s = requests.session()
    #
    # res = s.post(url=URL, data=BODY, headers=headers, verify=False)
    #
    # print res.json()
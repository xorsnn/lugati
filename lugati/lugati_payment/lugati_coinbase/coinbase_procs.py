import logging
import os
import hashlib
import hmac
import urllib2
import time
from django.conf import settings

def make_request(url, body=None):
    opener = urllib2.build_opener()
    nonce = int(time.time() * 1e6)
    message = str(nonce) + url + ('' if body is None else body)
    signature = hmac.new(settings.COINBASE_API_SECRET, message, hashlib.sha256).hexdigest()

    headers = {'ACCESS_KEY': settings.COINBASE_API_KEY,
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
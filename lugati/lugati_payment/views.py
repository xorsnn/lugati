# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from lugati.lugati_media.models import ThebloqImage
import json
import logging
import os
import hashlib
import hmac
import urllib2
import time
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_payment.models import BTCPaymentTransaction
from lugati.lugati_payment.forms import NgSendBitcoinsForm
from django.db.models import Count, Min, Sum, Avg
from django.conf import settings
from lugati.lugati_payment.lugati_coinbase.coinbase_procs import make_request
from decimal import *
from lugati.lugati_payment.payment_procs import get_btc_balance_proc, get_pending_btc_proc
from PIL import Image, ImageDraw, ImageFont
import qrcode
import StringIO
logger = logging.getLogger(__name__)
from django.core.files.uploadedfile import InMemoryUploadedFile
import stomp
from lugati.lugati_payment.lugati_coinbase.models import CoinbaseCallback, CallbackTickets
from lugati.lugati_shop import cart
from django.contrib.sites.models import get_current_site
import base64
from datetime import datetime, timedelta
from django.utils import timezone

stomp_conn = stomp.Connection()
stomp_conn.start()
stomp_conn.connect()

def get_btc_invoice(request):
    res_dt = {}
    cart_items = cart.get_cart_items(request)
    cart_id = ''
    cart_total = 0
    cart_total_btc = 0
    for cart_item in cart_items:
        cart_total += cart_item.total()
        cart_total_btc += cart_item.get_total_btc()
        if cart_id == '':
            cart_id = cart_item.cart_id

    callback_ticket = CallbackTickets()
    logger.info('creating ticket: ' + str(cart_id))
    callback_ticket.cart_id = str(cart_id)
    callback_ticket.site = get_current_site(request)
    callback_ticket.save()

    PAYMENT_CALLBACK_URL = 'http://merchant.mycelium.com/payment/lugati_coinbase/callback/'

    params = {"address": {
        'callback_url': PAYMENT_CALLBACK_URL + str(callback_ticket.id) + '/'
    }}

    if settings.SHOP_TYPE == 'MPS' and False:
        from lugati.lugati_payment.lugati_mycelium import payment_procs as mycelium_payment_procs
        res = mycelium_payment_procs.make_request(settings.MYCELIUM_API_URL + '/generate_receive_address', body=json.dumps(params)).read()
    else:
        res = make_request('https://api.coinbase.com/v1/account/generate_receive_address', body=json.dumps(params)).read()

    addr_dt = json.loads(res)
    logger.info('adr dt ->')
    logger.info(res)

    res_dt['addr_dt'] = addr_dt
    res_dt['custom'] = str(cart_id)
    res_dt['price'] = str(round(cart_total_btc, 5))
    return HttpResponse(json.dumps(res_dt))

def get_qr_code(request):
    res_dt = {}
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )

    qr.add_data(request.GET['link'])
    qr.make(fit=True)

    img = qr.make_image()
    (w, h) = img.size
    new_im = Image.new("RGB", (w, h), '#ffffff')
    new_im.paste(img, (0, 0))

    tempfile_io = StringIO.StringIO()
    new_im.save(tempfile_io, format='PNG')

    base64_str = base64.b64encode(tempfile_io.getvalue())

    res_dt['base64_str'] = base64_str

    return HttpResponse(json.dumps(res_dt))

def get_btc_balance_channel_address(request):
    res_dt = {}
    if request.user.is_authenticated():
        cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
        res_dt['session_id'] = 'btc_balance_' + str(cur_company.id)
    return HttpResponse(json.dumps(res_dt), content_type="application/json")

def send_btc(request):
    res_dt = {}
    form = NgSendBitcoinsForm(data=json.loads(request.body))

    if form.is_valid() and request.user.is_authenticated():
        cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
        bal_sum = float(get_btc_balance_proc(cur_company)-get_pending_btc_proc(cur_company))
        logger.info(bal_sum)
        to = form.cleaned_data['to']
        amount = float(form.cleaned_data['amount'])
        message = form.cleaned_data['message']

        logger.info('balance is: ' + str(bal_sum))
        logger.info('amount is: ' + str(amount))

        params = {
            "transaction": {
                "to": to,
                "notes": message
            }
        }

        can_send = False
        has_fee = False

        logger.info('amount:')
        logger.info(str(amount))

        if (bal_sum >= (amount + 0.0001)) and (amount <= 0.01):
            logger.info(1)
            can_send = True
            params['transaction']['amount'] = str(amount)
            params['transaction']['user_fee'] = "0.0001"
            has_fee = True
        elif (bal_sum >= amount) and (amount > 0.01):
            logger.info(2)
            can_send = True
            params['transaction']['amount'] = str(amount)
        logger.info('can send: ' + str(can_send))
        if can_send:
            res = make_request('https://api.coinbase.com/v1/transactions/send_money', body=json.dumps(params)).read()
            logger.info('res: ' + str(res))
            dict_res = json.loads(res)
            res_dt = {
                'success': dict_res['success'],
                'msg': "you successfully sent btc"
            }
            if dict_res['success']:
                btc_payment_transaction = BTCPaymentTransaction()
                btc_payment_transaction.company = cur_company
                btc_payment_transaction.sum = float(dict_res['transaction']['amount']['amount'])
                # if has_fee:
                #     btc_payment_transaction.sum -= 0.0001
                btc_payment_transaction.save()
            else:
                # try
                res_dt = {
                    'msg': "Error, please enter a valid bitcoin address."
                }
        else:

            res_dt = {
                'success': False,
                'msg': "you don't have enougth bitcoins"
            }

    else:
        res_dt = {
            'success': False,
            'msg': "you are not authenticated or have sent wrong data"
        }

    return HttpResponse(json.dumps(res_dt), content_type="application/json")


def get_btc_balance(request):
    res_dt = {}
    if request.user.is_authenticated():
        cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
        balance = BTCPaymentTransaction.objects.filter(company=cur_company).aggregate(Sum('sum'))
        bal_sum = balance['sum__sum']
        if not bal_sum:
            bal_sum = Decimal(0)
        res_dt = {
            'balance': "%.8f" % bal_sum
        }
        #pending btc
        delta = timedelta(seconds=settings.TRANSACTONS_PENDING_TIME_SECONDS)
        pending_balance = BTCPaymentTransaction.objects.filter(company=cur_company).filter(sum__gt=0).filter(dt_add__gt=timezone.now()-delta).aggregate(Sum('sum'))
        pending_bal_sum = pending_balance['sum__sum']
        if not pending_bal_sum:
            pending_bal_sum = Decimal(0)
        res_dt['pending_balance'] = "%.8f" % pending_bal_sum
    else:
        res_dt = {
            'error': 'user is not authenticated'
        }
    return HttpResponse(json.dumps(res_dt))
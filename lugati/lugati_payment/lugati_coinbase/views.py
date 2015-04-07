# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from lugati.products.models import Product, Brand

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from lugati.lugati_shop import cart
from lugati.lugati_shop.lugati_orders.models import Order, OrderItem
from django.template import Context

from django.shortcuts import redirect
from django.template.loader import get_template
import json
import datetime
from gcm import GCM

from django.contrib.sites.models import get_current_site
from django.http import Http404
from django.core.urlresolvers import resolve
from twilio.rest import TwilioRestClient

from django.views.decorators.csrf import csrf_exempt
from coinbase import CoinbaseAccount
from .models import CoinbaseCallback, CallbackTickets
from lugati.lugati_shop import cart
from lugati.lugati_shop.lugati_cart.models import CartItem

from lugati.lugati_mobile.models import LugatiDevice
import logging
from lugati.lugati_shop.models import ShoppingPlace, Shop, LugatiClerk, LugatiCompany, LugatiShoppingSession

import stomp
from lugati.lugati_payment.models import BTCPaymentTransaction

logger = logging.getLogger(__name__)

client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

gcm = GCM(settings.GCM_APIKEY)

from lugati.lugati_payment.lugati_coinbase.coinbase_procs import make_request
from lugati.lugati_payment.payment_procs import get_btc_balance_proc


stomp_conn = stomp.Connection()
stomp_conn.start()
stomp_conn.connect()


@csrf_exempt
def check_if_order_paid(request):
    res_dt = {
        'paid': False
    }
    if not cart.get_cart_items(request).exists():
        orders = Order.objects.filter(cart_id=cart._cart_id(request))
        if orders.exists():
            res_dt['order_id'] = orders[0].id
        res_dt['paid'] = True

    return HttpResponse(json.dumps(res_dt))


def get_coinbase_invoce(request):
    cart_items = cart.get_cart_items(request)
    cart_id = ''
    cart_total = 0
    cart_total_btc = 0
    for cart_item in cart_items:
        cart_total += cart_item.total()
        cart_total_btc += cart_item.get_total_btc()
        if cart_id == '':
            cart_id = cart_item.cart_id

    res_dt = {}

    callback_ticket = CallbackTickets()
    logger.info('creating ticket: ' + str(cart_id))
    callback_ticket.cart_id = str(cart_id)
    callback_ticket.site = get_current_site(request)
    callback_ticket.save()

    # addr_dt = account.generate_receive_address(str(callback_ticket.id))
    PAYMENT_CALLBACK_URL = 'http://merchant.mycelium.com/payment/lugati_coinbase/callback/'
    params = {"address": {
        'callback_url': PAYMENT_CALLBACK_URL + str(callback_ticket.id) + '/'
    }}
    res = make_request('https://api.coinbase.com/v1/account/generate_receive_address', body=json.dumps(params)).read()
    addr_dt = json.loads(res)

    res_dt['addr_dt'] = addr_dt
    res_dt['custom'] = str(cart_id)
    # res_dt['price'] = str(cart_total)
    # remove !!!!
    # res_dt['price'] = str(0.0001)
    res_dt['price'] = str(round(cart_total_btc, 5))
    return HttpResponse(json.dumps(res_dt))


# #send_to_waiter
# def send_notofication(msg = ''):
# #xmpp
# #your_jid = 'xors.nn@gmail.com'
#     #your_password = 'OhN3Ag3Uid'
#     your_jid = 'lugatiname1@gmail.com'
#     your_password = 'gmujnm567'
#     target_jid = 'xors.nn@gmail.com'
#     if msg == '':
#         message = 'http://lugati.ru:9004/catalog/point_of_sale/2/#/order_details/37'
#     else:
#         message = msg
#     send_message(your_jid, your_password, target_jid, message)
#     #~xmpp
# #

# @csrf_exempt
# def coinbase_callback_testing(request):
#     logger.info('test1  !')
#     send_notofication()
#     return HttpResponse()

@csrf_exempt
def coinbase_callback(request, ticket=''):
    logger.info('ticket -> ' + ticket)
    if request.method == 'POST':

        logger.info('trying body')

        try:
            c_callback = CoinbaseCallback()
            c_callback.callback_body = str(request.body)
            c_callback.save()
            logger.info(str(request.body))
        except:
            logger.info('try failed')

        data = json.loads(request.body)

        if ticket <> '':
            logger.info('trying create payment transaction')
            try:
                sum = 0
                callback_ticket = CallbackTickets.objects.get(pk=ticket)
                site = callback_ticket.site
                order = cart.make_order_paid(callback_ticket.cart_id)

                try:
                    payment_dt = json.loads(request.body)
                    btc_payment_transaction = BTCPaymentTransaction()
                    btc_payment_transaction.company = order.shopping_place.shop.company
                    btc_payment_transaction.sum = payment_dt['amount']
                    btc_payment_transaction.save()
                    # if order.shopping_place:
                    #     stomp_conn.send(body=json.dumps({'message': 'btc_balance_changed', 'btc_balance': get_btc_balance_proc(order.shopping_place.shop.company)}),
                    #                     destination='/topic/' + 'btc_balance_' + str(order.shopping_place.shop.company.id))
                except:
                    logger.info('failed to create transaction')

                if (order):
                    #xmpp
                    logger.info('devices' + '1')
                    clerks = LugatiClerk.objects.filter(company=order.shopping_place.shop.company)
                    for clerk in clerks:
                        try:
                            logger.info('trying sending notification')
                            data = {
                                'title': order.shopping_place.shop.company.name,
                                'message': "order " + str(order.id) + " paid (" + str(order.shopping_place) + ")",
                                'timeStamp': datetime.datetime.now().isoformat(),
                                'type': 'new_order',
                                'order_id': str(order.id)
                            }
                            gcm.plaintext_request(registration_id=clerk.reg_id, data=data)
                        except Exception, e:
                            logger.info('exception: ' + str(e))

                    #~xmpp

                    # channel = 'client_payment_channel_' + str(LugatiShoppingSession.objects.filter(cart_id=order.cart_id)[0].id)
                    # # channel = 'all_clients'
                    stomp_conn.send(body=json.dumps({'message': 'order_paid', 'order': order.get_list_item_info()}),
                                    destination='/topic/' + 'payment_channel_' + str(
                                        LugatiShoppingSession.objects.filter(cart_id=order.cart_id)[0].id))
            except Exception, e:
                logger.info('err -> ' + str(e))

    return HttpResponse()



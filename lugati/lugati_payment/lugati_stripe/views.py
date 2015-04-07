from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json
from lugati.lugati_shop.models import LugatiCompany, ShoppingPlace
from lugati.lugati_registration.models import LugatiUserProfile
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import resolve
import stripe
import lugati.lugati_shop.cart as cart
import datetime
import stomp
from django.conf import settings
from lugati.lugati_shop.models import LugatiClerk, LugatiShoppingSession
import logging
from lugati.lugati_payment.payment_procs import get_currency_exchange_rate_proc
from gcm import GCM
from lugati import lugati_procs
import requests

gcm = GCM(settings.GCM_APIKEY)
logger = logging.getLogger(__name__)

stomp_conn = stomp.Connection()
stomp_conn.start()
stomp_conn.connect()

def stripe_connect(request):
    logger.info(request.GET)
    # {u'scope': [u'read_write'], u'state': [u'1234'], u'code': [u'ac_5udJNt94jFGAMUTq9zHfMHM6OZuLKkCw']}
    company = None
    if request.user.is_authenticated():
        prof = LugatiUserProfile.objects.get(user=request.user)
        company = prof.get_company()

    if ('code' in request.GET) and request.user.is_authenticated():
        try:
            params = {
                'client_secret': settings.STRIPE_API_SECRET,
                'code': request.GET['code'],
                'grant_type': 'authorization_code'
            }
            res = requests.post('https://connect.stripe.com/oauth/token', data=params)
            # {u'stripe_publishable_key': u'pk_test_NfDiiEzMy8XjdF4DDqd5I5dJ', u'access_token': u'sk_test_2q0T3Rkz1pPunULdQjQNjKfp', u'livemode': False, u'token_type': u'bearer', u'scope': u'read_write', u'refresh_token': u'rt_5udVzaORHkyL8SFhE5nFCkpu2AxoIk24ck3v4XcGjR6bRE8n', u'stripe_user_id': u'acct_15JSsdKJjduWQTvD'}
            res_dt = res.json()
            logger.info(str(res_dt))
            company.stripe_public_key = res_dt['stripe_publishable_key']
            company.stripe_secret_key = res_dt['access_token']
            company.save()
            logger.info(res.json())
            return HttpResponseRedirect('/lugati_admin/#/edit/' + str(lugati_procs.get_content_type_id_by_name('LugatiCompany')) + '/' + str(company.id))
        except Exception, e:
            logger.info(str(e))

    # return HttpResponse(json.dumps({'message': 'something went wrong!'}))
    if request.user.is_authenticated() and company:
        try:
            return HttpResponseRedirect('/lugati_admin/#/edit/' + str(lugati_procs.get_content_type_id_by_name('LugatiCompany')) + '/' + str(company.id))
        except:
            return HttpResponseRedirect('/lugati_admin/')
    return HttpResponseRedirect('/lugati_admin/')

def get_public_key(request):
    resp_dt = {}

    cur_company = None

    if 'cur_path' in request.GET:
        resolved_path = resolve(request.GET['cur_path'])
        try:
            pos_id = resolved_path.kwargs['pos_id']
            place = ShoppingPlace.objects.get(pk=pos_id)
            cur_company = place.shop.company
        except:
            if request.user.is_authenticated():
                from lugati.lugati_registration.models import LugatiUserProfile
                cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()

    if cur_company:
        try:
            stripe.api_key = cur_company.stripe_secret_key
            stripe.Account.retrieve()

            resp_dt['stripe_public_key'] = cur_company.stripe_public_key
            resp_dt['company_name'] = cur_company.name
            resp_dt['currency_str'] = cur_company.default_currency.stripe_str
            resp_dt['usd_rate'] = get_currency_exchange_rate_proc(cur_company.default_currency.stripe_str, 'usd').get_list_item_info()
        except:
            pass

    return HttpResponse(json.dumps(resp_dt))

@csrf_exempt
def stripe_callback(request):

    # todo
    res_dt = {}
    cur_company = None
    if 'cur_path' in request.GET:
        resolved_path = resolve(request.GET['cur_path'])
        try:
            pos_id = resolved_path.kwargs['pos_id']
            place = ShoppingPlace.objects.get(pk=pos_id)
            cur_company = place.shop.company
        except:
            if request.user.is_authenticated():
                from lugati.lugati_registration.models import LugatiUserProfile
                cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()

    if cur_company:
        stripe.api_key = cur_company.stripe_secret_key
        # Get the credit card details submitted by the form
        token = request.GET['stripe_token']
        # Create the charge on Stripe's servers - this will charge the user's card
        cart_id = cart._cart_id(request)
        order = None
        order = cart.make_order_paid(cart_id)
        try:
            charge = stripe.Charge.create(
                amount=int(order.get_total_sum()*100),
                currency=cur_company.default_currency.stripe_str,
                card=token,
                description="order #" + str(order.id)
            )
            logger.info('charge :')
            logger.info(charge)
        except Exception, e:
            logger.info('charge err')
            if order:
                from lugati.lugati_shop.lugati_orders.models import OrderState
                order.state = OrderState.objects.get(name='CANCELLED&REFUNDED', custom_id=4)
                order.save()
            res_dt['success'] = False

        if (order):
            res_dt['success'] = True
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

            stomp_conn.send(body=json.dumps({'message': 'order_paid', 'order': order.get_list_item_info()}), destination='/topic/' + 'payment_channel_' + str(LugatiShoppingSession.objects.filter(cart_id=order.cart_id)[0].id))



    return HttpResponse(json.dumps(res_dt))
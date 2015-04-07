# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import json
from django.contrib.sites.models import get_current_site
from lugati.lugati_shop import cart
from django.conf import settings
from lugati.lugati_shop.lugati_delivery.models import DeliveryOption, DeliveryPrice
import decimal
import logging
from django.core.urlresolvers import resolve
from django.views.decorators.csrf import csrf_exempt
from lugati.lugati_shop.lugati_delivery.views import get_delivery_opts
from lugati.products.models import Product
from lugati.lugati_shop.lugati_cart.models import CartItem

logger = logging.getLogger(__name__)

@csrf_exempt
def can_add_to_cart(request, prod_id=''):
    res_dt = {
        'result': 'success'
    }

    if cart.get_cart_items(request).count() > 0:
        opts_dt = get_delivery_opts(request, new_product=Product.objects.get(pk=prod_id))
        if (not opts_dt['can_continue']):
            res_dt['result'] = 'error'

    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def api_cart_items(request, cart_item_id=''):
    cur_site = get_current_site(request)
    resp_dt = {}
    if cart_item_id == '':
        if request.method == 'POST':
            body_dt = json.loads(request.body)
            prod_id = body_dt['prod_id']
            quantity = body_dt['quantity']

            try:
                pos_id = resolve(body_dt['cur_url']).kwargs['pos_id']
            except:
                pos_id = None

            if not 'options' in body_dt:
                body_dt['options'] = None

            if 'cart_item_assigned' in body_dt:
                cart_item = cart.add_product_to_cart(request,
                                                     prod_id=prod_id,
                                                     quantity=quantity,
                                                     pos_id=pos_id,
                                                     options=body_dt['options'],
                                                     cart_item_assigned=body_dt['cart_item_assigned'])
            else:
                cart_item = cart.add_product_to_cart(request, prod_id=prod_id, quantity=quantity, pos_id=pos_id, options=body_dt['options'])
                # cart_item.cart_item_assigned = CartItem.objects.get(pk=body_dt['cart_item_assigned'])
                # cart_item.save()
            resp_dt = cart_item.get_list_item_info(request)

        elif request.method == 'GET':
            resp_dt = []
            cart_items = cart.get_cart_items_with_toppings(request)
            cart_products = []

            total_cart_items = 0

            for cart_item in cart_items:
                node = cart_item.get_list_item_info(request)

                cart_products.append(cart_item.product)

                node['images'] = []

                if 'thumbnail_size_str' in request.GET:
                    thumbnail_size_str = request.GET['thumbnail_size_str']
                    for img in cart_item.product.get_images():
                        img_node={}
                        img_node['image_url'], img_node['image_margin'] = img.get_thumbnail_attributes(img.get_thumbnail(thumbnail_size_str, get_native_image=True),thumbnail_size_str)
                        node['images'].append(img_node)
                resp_dt.append(node)
                total_cart_items += cart_item.quantity

            node = {}

            #todo delivery
            node['online_payment'] = True

            total_delivery_price = cart.get_total_delivery_price(request)

            delivery_cart_options = cart.get_all_cart_delivery(request)
            if delivery_cart_options.exists():

                # total_delivery_cost += delivery_cart_option.delivery_option.price
                # total_delivery_additional_cost += delivery_cart_option.delivery_option.additional_price

                #todo online payment
                node['online_payment'] = delivery_cart_options[0].delivery_option.online_payment

                # try:
                #     total_delivery_price = total_delivery_cost + ((total_cart_items-1) * total_delivery_additional_cost)
                # except Exception, e:
                #     logger.info(str(e))
            else:
                delivery_options = DeliveryOption.objects.filter(site=cur_site)
                if delivery_options.exists():
                    total_delivery_price = delivery_options[0].price

            if settings.DEFAULT_CURRENCY == 'BTC':
                node['total_delivery_price'] = "%.8f" % total_delivery_price
            else:
                node['total_delivery_price'] = "%.2f" % total_delivery_price
            resp_dt.append(node)
            #~todo delivery
    else:
        if request.method == 'PUT':
            # only implemented for quantity change
            instance = CartItem.objects.get(pk=cart_item_id)
            body_dt = json.loads(request.body)
            instance.augment_quantity(body_dt['quantity'] - instance.quantity)
            resp_dt['message'] = 'done'
        else:
            resp_dt['message'] = 'not implemented yet'
    return HttpResponse(json.dumps(resp_dt))

from django.shortcuts import render
from .models import DeliveryOption, City, DeliveryPrice

from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.http import HttpResponse
import json
from django.contrib.sites.models import get_current_site
from .forms import DeliveryOptionForm
from lugati.lugati_shop import cart
import logging
logger = logging.getLogger(__name__)

def get_delivery_opts(request, region_id='', new_product=None):
    res_dt = {}
    cur_site = get_current_site(request)

    # city = City.objects.get(pk=region_id)

    if region_id == '':
        cities = City.objects.filter(site=cur_site)
    else:
        cities = City.objects.filter(pk=region_id)

    cart_items = cart.get_cart_items(request)
    products = []
    for item in cart_items:
        products.append(item.product)
    if new_product:
        products.append(new_product)

    delivery_options = DeliveryOption.objects.filter(active=True).filter(Q(city__in=cities) | Q(city=None)).filter(
        site=cur_site)

    res_dt['delivery_options'] = []
    for delivery_option in delivery_options:
        logger.info(str(delivery_option))
        checked_products = []

        pr = 0
        additional_pr = 0
        try:
            delivery_prices = DeliveryPrice.objects.filter(delivery_option=delivery_option, product__in=products)
        except:
            delivery_prices = DeliveryPrice.objects.none()

        for delivery_price in delivery_prices:
            pr = delivery_price.price
            additional_pr = delivery_price.additional_price
            if delivery_price.product not in checked_products:
                checked_products.append(delivery_price.product)
        if len(checked_products) == len(products):
            res_dt['delivery_options'].append({
                'id': delivery_option.id,
                'name': delivery_option.name,
                #'price': "{:.2f}".format(float(delivery_option.price)),
                #'additional_price': "{:.2f}".format(float(delivery_option.additional_price)),
                'price': "{:.2f}".format(float(pr)),
                'additional_price': "{:.2f}".format(float(additional_pr)),
                'online_payment': delivery_option.online_payment
            })
    if len(res_dt['delivery_options']) > 0:
        res_dt['can_continue'] = True
    else:
        res_dt['can_continue'] = False
    return res_dt

def get_delivery_options(request, region_id=''):

    res_dt = get_delivery_opts(request, region_id)

    return HttpResponse(json.dumps(res_dt))

def lugati_update_delivery_option(request, delivery_option_id=''):
    #todo!!!!!!
    cart.get_all_cart_delivery(request).delete()
    # de
    # region = City.objects.get(pk=delivery_option_id)
    # delivery_option = DeliveryOption.objects.get(city=region)
    delivery_option = DeliveryOption.objects.get(pk=delivery_option_id)

    cart.add_delivery_option(request, delivery_option)

    return HttpResponse(json.dumps({}))

# -*- coding: utf-8 -*-
from django import template
register = template.Library()

from django.template import Library, Node, TemplateSyntaxError
from lugati.products.models import Product
from lugati.lugati_shop import cart
from lugati.lugati_shop.forms import CofirmOrderForm, LugatiCofirmOrderForm
import random
from django.db.models import Count

from django.contrib.sites.models import get_current_site
from django.conf import settings
register = Library()

@register.inclusion_tag('lugati_shop/lugati_cart_block.html', takes_context = True)
def lugati_cart_block(context):
    res_dt = {}
    cart_items = cart.get_cart_items(context['request'])
    res_dt['cart_items'] = cart_items
    return res_dt

@register.inclusion_tag('lugati_shop/cart_block.html', takes_context = True)
def cart_block(context):
    res_dt = {}
    cart_items = cart.get_cart_items(context['request'])
    res_dt['cart_items'] = cart_items
    return res_dt

@register.inclusion_tag('lugati_shop/cart_block_with_delivery.html', takes_context = True)
def cart_block_with_delivery(context):
    res_dt = {}
    cart_items = cart.get_cart_items(context['request'])
    res_dt['cart_items'] = cart_items
    return res_dt

@register.inclusion_tag('lugati_shop/cart_block_wo_delivery.html', takes_context = True)
def cart_block_wo_delivery(context):
    res_dt = {}
    cart_items = cart.get_cart_items(context['request'])
    res_dt['cart_items'] = cart_items
    res_dt['wo_delivery'] = True
    return res_dt

@register.inclusion_tag('lugati_shop/delivery_block.html', takes_context = True)
def delivery_block(context):
    res_dt = {}
    #cart_items = cart.get_cart_items(context['request'])
    #res_dt['cart_items'] = cart_items
    return res_dt
#deprecated
@register.inclusion_tag('lugati_shop/confirm_order_form.html', takes_context = True)
def confirm_order_form(context):
    res_dt = {
        'form': CofirmOrderForm,
    }
    cart_items = cart.get_cart_items(context['request'])

    if cart_items.count() > 0:
        res_dt['has_items'] = True
    else:
        res_dt['has_items'] = False

    return res_dt
#~deprecated

@register.inclusion_tag('lugati_shop/confirm_order_form_bootstrap.html', takes_context = True)
def confirm_order_form_bootstrap(context):
    res_dt = {
        'form': LugatiCofirmOrderForm,
    }
    cart_items = cart.get_cart_items(context['request'])

    if cart_items.count() > 0:
        res_dt['has_items'] = True
    else:
        res_dt['has_items'] = False

    return res_dt



@register.inclusion_tag('lugati_shop/global_cart_content.html', takes_context = True)
def get_cart_global(context):
    res_dt = {}
    #cart_items = cart.get_cart_items(context['request'])
    #res_dt['cart_items'] = cart_items
    res_dt['cart_items'] = []
    return res_dt

@register.filter
def get_total_price(instance):
    total_price = 0
    for cart_item in instance:
        total_price += cart_item.total()
    return str('%.2f' % (total_price,))

@register.filter
def lugati_get_product_details_url(instance):
    return '/catalog/product_details/' + str(instance.id)

#@register.simple_tag(takes_context=True)
#def lugati_get_product_details_url(context, instance):
#    request = context['request']
#    lugati_base_url = request.path
#    cur_site = get_current_site(request)
#
#    return '/catalog/product_details/' + instance.id


#{% with "/catalog/product_details/"|add:product_id as product_url %}
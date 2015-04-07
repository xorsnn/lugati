# -*- coding: utf-8 -*-
from django import template
register = template.Library()

from django.template import Library, Node, TemplateSyntaxError
from lugati.products.models import Product
from lugati.lugati_shop import cart
from lugati.lugati_shop.forms import CofirmOrderForm, LugatiCofirmOrderForm
import random
from django.db.models import Count
from django.core.urlresolvers import resolve
from django.contrib.sites.models import get_current_site
from django.conf import settings
from lugati.lugati_shop.models import ShoppingPlace
register = Library()

@register.inclusion_tag('lugati_shop/settings/lugati_styles.html', takes_context = True)
def lugati_shop_styles(context):
    res_dt = {}
    request = context['request']
    match = resolve(request.path)
    place = ShoppingPlace.objects.get(pk=match.kwargs['pos_id'])
    #set = ShopSetting.objects.get(shop=place.shop)
    res_dt['background_color'] = place.shop.background_color
    res_dt['color'] = place.shop.text_color
    res_dt['font'] = place.shop.text_font
    return res_dt
#
@register.inclusion_tag('lugati_shop/settings/lugati_logo_block.html', takes_context = True)
def lugati_logo_block(context):
    res_dt = {}
    request = context['request']
    cur_site = get_current_site(request)
    if cur_site.name == 'mps':
        res_dt['path_to_logo'] = '/media/custom/mps/img/lugati_default/default_logo.png'
        res_dt['logo_height'] = 100
    else:
        res_dt['logo_block_style'] = 'background-color:#5dafc6'
        res_dt['path_to_logo'] = '/media/lugati_admin/img/logo.png'
        res_dt['logo_height'] = 100
    return res_dt
# @register.inclusion_tag('lugati_shop/settings/lugati_logo_block.html', takes_context = True)
# def lugati_logo_block_clean(context):
#     res_dt = {}
#     request = context['request']
#     cur_site = get_current_site(request)
#     res_dt['request'] = request
#     res_dt['user'] = request.user
#     if cur_site.name == 'mps':
#         res_dt['path_to_logo'] = 'http://lugati.ru' + '/media/custom/mps/img/lugati_default/default_logo.png'
#         res_dt['logo_width'] = 300
#     else:
#         res_dt['logo_block_style'] = 'background-color:#5dafc6'
#         res_dt['path_to_logo'] = 'http://lugati.ru' + '/media/lugati_admin/img/logo.png'
#         res_dt['logo_height'] = 300
#     return res_dt


# -*- coding: utf-8 -*-
from django import template
register = template.Library()

from django.template import Library, Node, TemplateSyntaxError
from lugati.products.models import Product, ProductPropertyValue
#from shop.models import Promo, ProdutOfTheMonth
from lugati.lugati_shop import cart
from lugati.lugati_shop.forms import CofirmOrderForm
import random
from django.db.models import Count
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.core.urlresolvers import resolve, reverse

register = Library()

@register.assignment_tag(takes_context=True)
def products_list(context, category_id=None):
    request = context['request']
    cur_site = get_current_site(request)
    if category_id:
        try:
            category = Product.objects.get(pk=category_id)
            products = Product.objects.filter(is_category=False).filter(site=cur_site).filter(parent_object=category)
        except:
            products = Product.objects.none()
    else:
        products = Product.objects.filter(is_category=False).filter(site=cur_site)
    return products

@register.inclusion_tag('products/templatetags/lugati_product_properties_block.html', takes_context=True)
def lugati_product_properties_block(context):
    request = context['request']
    cur_site = get_current_site(request)

    res_dt = {
        'LUGATI_MODULES': settings.LUGATI_MODULES,
        'objects_list': ProductPropertyValue.objects.filter(product=request.GET['prod_id'])
    }

    return res_dt

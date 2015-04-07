# -*- coding: utf-8 -*-

from lugati.products.models import Product, Bestseller

from django.template import Library, Node, TemplateSyntaxError
from django.contrib.sites.models import get_current_site

from lugati.lugati_points_of_sale.models import City
register = Library()

@register.inclusion_tag('lugati_points_of_sale/nearest_point.html', takes_context=True)
def lugati_nearest_pos(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    return {
        'cities': City.objects.filter(site=cur_site),
        'np_city': True,
        'np_point': True

    }

@register.inclusion_tag('lugati_points_of_sale/nearest_point.html', takes_context=True)
def lugati_nearest_pos_city(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    return {
        'cities': City.objects.filter(site=cur_site),
        'np_city': True,
        'np_point': False
    }

@register.inclusion_tag('lugati_points_of_sale/nearest_point.html', takes_context=True)
def lugati_nearest_pos_point(context):
    from lugati.lugati_procs import get_ids
    request = context['request']
    cat_id, prod_id = get_ids(request)
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    return {
        'cities': City.objects.filter(site=cur_site),
        'np_city': False,
        'np_point': True
    }
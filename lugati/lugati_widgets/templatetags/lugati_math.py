# -*- coding: utf-8 -*-

from lugati.products.models import Product, Bestseller
from django.conf import settings
from django.template import Library, Node, TemplateSyntaxError
from django.contrib.sites.models import get_current_site
from lugati.lugati_shop.lugati_promo.models import SpecialOffer
import os
from lugati.products.models import Brand
from django.core.urlresolvers import resolve
from lugati.lugati_media.lugati_gallery.models import SliderItem
from lugati.lugati_widgets.models import LugatiTextBlock
from lugati import lugati_procs
from django.contrib.contenttypes.models import ContentType

register = Library()


@register.filter
def lugati_modulo(value, arg):
    return value % arg

# register.filter('cut', cut)

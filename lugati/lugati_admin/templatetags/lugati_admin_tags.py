# -*- coding: utf-8 -*-
from django import template
register = template.Library()
from django.utils.translation import ugettext as _
from django.template import Library, Node, TemplateSyntaxError
from lugati.products.models import Product
#from shop.models import Promo, ProdutOfTheMonth
from lugati.lugati_shop import cart
from lugati.lugati_shop.forms import CofirmOrderForm
import random
from django.db.models import Count
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from lugati import lugati_procs
from lugati.lugati_registration.models import LugatiUserProfile, LugatiRole
from lugati.lugati_shop.models import ShoppingPlace
from django.contrib.sites.models import Site

from django.core.urlresolvers import resolve, reverse
register = Library()

# @register.inclusion_tag('lugati_admin/lugati_version_1_0/include/raw_title.html', takes_context=True)
# def lugati_payment_qr_code_header(context):
#     request = context['request']
#     cur_site = get_current_site(request)
#     res_dt = {
#         'title': 'top'
#     }
#     return res_dt
#
# @register.inclusion_tag('lugati_admin/lugati_version_1_0/include/raw_title.html', takes_context=True)
# def lugati_payment_qr_code_footer(context):
#     request = context['request']
#     cur_site = get_current_site(request)
#     res_dt = {
#         'title': 'bottom'
#     }
#     return res_dt

@register.inclusion_tag('lugati_admin/lugati_version_1_0/include/mps_admin_pannel.html', takes_context=True)
def lugati_admin_menu_tag(context):
    request = context['request']
    cur_site = get_current_site(request)

    res_dt = {
        'user': request.user
    }

    resolved_path = resolve(request.path)

    if request.user.is_authenticated():
        prof = LugatiUserProfile.objects.get(user=request.user)
        company = prof.get_company()
    else:

        if 'pos_id' in resolved_path.kwargs:
            company = ShoppingPlace.objects.get(pk=resolved_path.kwargs['pos_id']).shop.company
        else:
            company = None

    if 'pos_id' in resolved_path.kwargs:
        res_dt['pos_id'] = resolved_path.kwargs['pos_id']

    res_dt['LUGATI_MODULES'] = settings.LUGATI_MODULES
    res_dt['SHOP_TYPE'] = settings.SHOP_TYPE

    if company:
        res_dt['company_settings_link'] = '/edit/' + str(lugati_procs.get_content_type_id_by_name('LugatiCompany')) + '/' + str(company.id)

    if request.user.is_authenticated():
        role = LugatiRole.objects.get(name='waiter')
        if role in prof.roles.all():
            res_dt['is_waiter'] = True
        else:
            res_dt['is_waiter'] = False
    else:
        res_dt['is_waiter'] = False

    return res_dt

def render(element, markup_classes):
    element_type = element.__class__.__name__.lower()

@register.filter
def lugati_to_angular_model(element):
    #markup_classes = {'label': '', 'value': '', 'single_value': ''}
    #return render(element, markup_classes)
    return element


@register.inclusion_tag('lugati_admin/templatetags/mps_logo_block.html', takes_context=True)
def mps_logo_block(context):
    request = context['request']
    cur_site = get_current_site(request)

    res_dt = {
        'LUGATI_MODULES': settings.LUGATI_MODULES
    }

    res_dt['request'] = request

    cur_company = None
    if request.user.is_authenticated():
        cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
    else:
        resolved_path = resolve(request.path)
        if 'pos_id' in resolved_path.kwargs:
            order_point = ShoppingPlace.objects.get(pk=resolved_path.kwargs['pos_id'])
            cur_company = order_point.shop.company

    if cur_company:
        res_dt['logo_url'] = cur_company.get_logo_url(request=request)
        res_dt['logo_attributes'] = cur_company.get_logo_attributes()
    else:
        res_dt['logo_attributes'] = {
            'menu_padding': '70px',
            'logo_padding': '15px 0'
        }
        if settings.SITE_ID == 6:
            res_dt['logo_url'] = '/media/custom/mps/img/small_logo.png'
        else:
            res_dt['logo_url'] = '/media/custom/lugati_site/img/logo_small.png'

    return res_dt

@register.inclusion_tag('lugati_admin/templatetags/lugati_admin_top_panel.html', takes_context=True)
def lugati_admin_top_panel(context):
    request = context['request']
    cur_site = get_current_site(request)
    res_dt = {
        'LUGATI_MODULES': settings.LUGATI_MODULES
    }
    res_dt['test_translate'] = _('main')
    res_dt['request'] = request
    return res_dt

@register.simple_tag
def lugati_active_link(request, url, class_name='active'):
    if url == '/':
        if url == request.path:
            return class_name
    elif request.path.startswith(url):
        return class_name
    return ''

@register.simple_tag
def lugati_get_content_type_id(model_name):
    return lugati_procs.get_content_type_id_by_name(model_name)

@register.assignment_tag
def lugati_get_content_type_id_assigment(model_name):
    return lugati_procs.get_content_type_id_by_name(model_name)

@register.assignment_tag
def get_lugati_objects(content_type_id, parent_object = None):
    model_class = ContentType.objects.get(pk=content_type_id).model_class()
    if parent_object:
        return model_class.objects.filter(parent_object=parent_object)
    else:
        return model_class.objects.all()


#roles
@register.assignment_tag
def lugati_has_right(request, model_name):
    from lugati.lugati_registration.models import LugatiRole
    if request.user.is_authenticated():
        prof = lugati_procs.get_user_profile(request.user)
        role = LugatiRole.objects.get(name='postman')
        if role in prof.roles.all():
            if model_name == 'Order':
                return True
            else:
                return False
        else:
            return True
    else:
        return False

@register.inclusion_tag('lugati_shop/settings/lugati_header_logo_block.html', takes_context = True)
def lugati_header_logo_block(context):
    res_dt = {}
    request = context['request']
    cur_site = get_current_site(request)
    res_dt['request'] = request
    res_dt['user'] = request.user
    if cur_site.name == 'mps':
        res_dt['path_to_logo'] = '/media/custom/mps/img/lugati_default/default_logo.png'
        res_dt['logo_height'] = 50

    else:
        res_dt['path_to_logo'] = '/media/lugati_admin/img/logo.png'
        res_dt['logo_height'] = 50
        res_dt['top_panel_block'] = '#141449'

    return res_dt

@register.simple_tag
def get_cur_domain():
    return settings.POS_SERVER

@register.simple_tag
def get_static_path():
    return settings.STATIC_ROOT


@register.simple_tag
def is_lugati_editing():
    return settings.POS_SERVER

@register.simple_tag
def get_cur_logo():
    site = Site.objects.get(pk=settings.SITE_ID)
    if site.name == 'mps':
        return settings.POS_SERVER + '/media/custom/mps/img/small_logo.png'
    else:
        return settings.POS_SERVER + '/media/custom/lugati_site/img/logo_small.png'


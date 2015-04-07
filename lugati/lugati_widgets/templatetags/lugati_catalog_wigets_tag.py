# -*- coding: utf-8 -*-

from lugati.products.models import Product, Bestseller
from django.conf import settings
from django.template import Library, Node, TemplateSyntaxError
from django.contrib.sites.models import get_current_site
import os
from lugati.products.models import Brand
from django.core.urlresolvers import resolve
from lugati.lugati_shop import cart

register = Library()



def get_ids(request):

    match = resolve(request.path)

    prod_id = ''
    cat_id = ''

    if 'prod_id' in match.kwargs:
        prod_id = match.kwargs['prod_id']
    if 'cat_id' in match.kwargs:
        cat_id = match.kwargs['cat_id']

    if cat_id == '':
        if 'cat_id' in request.GET:
            cat_id = request.GET['cat_id']
        #deprecated
        if cat_id == '':
            if 'parent_product' in request.GET:
                cat_id = request.GET['parent_product']
        #deprecated
        if cat_id == '':
            if 'category' in request.GET:
                cat_id = request.GET['category']

    if prod_id == '':
        if 'prod_id' in request.GET:
            prod_id = request.GET['prod_id']

        #deprecated
        if prod_id == '':
            if 'product_id' in request.GET:
                cat_id = request.GET['product_id']
        #deprecated

    return cat_id, prod_id

@register.inclusion_tag('widgets/shop/brand_menu.html', takes_context=True)
def lugati_brand_menu(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    brands = None
    match = resolve(request.path)
    if match.url_name == 'catalog_page':
        cat_id, prod_id = get_ids(request)
        brands = Brand.objects.filter(pk__in=set(Product.objects.filter(site=cur_site).filter(parent_object=cat_id).values_list('brand', flat=True).distinct())).order_by('name')
    elif match.url_name == 'product_details':
        brands = Brand.objects.filter(pk__in=set(Product.objects.filter(site=cur_site).filter(parent_object=Product.objects.get(pk=match.kwargs['prod_id']).parent_object).values_list('brand', flat=True).distinct())).order_by('name')
        lugati_base_url = '/catalog/' + str(Product.objects.get(pk=match.kwargs['prod_id']).parent_object.id) + '/'

    return {
        'lugati_base_url': lugati_base_url,
        'brands': brands
    }

@register.inclusion_tag('lugati_shop/catalog/product_details.html', takes_context = True)
def lugati_product_details(context):
    res_dt = {}
    request = context['request']
    cur_site = get_current_site(request)
    product = None
    cat_id, prod_id = get_ids(request)

    product = Product.objects.get(pk=prod_id)

    res_dt['product'] = product

    return res_dt

@register.inclusion_tag('lugati_shop/categories_menu.html', takes_context=True)
def lugati_categories_menu(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    lugati_base_url = settings.LUGATI_CATALOG_URL

    list_classes = []
    list_elements_classes = []
    ul_id = ''
    #deprecated!!!
    if cur_site.name == 'primorsk':
        list_classes = ['VMmenu', 'droplist']
        list_elements_classes = ['VmClose']
    elif cur_site.name == 'makemake.us':
        list_elements_classes = ['level-top', 'parent']
        ul_id = 'nav'
    #

    def format_name(name):
        #name.strip().replace('  ',' ').replace(' ', '<br>')
        ms = name.strip().replace('  ',' ').split(' ')
        res = ''
        for i in range(len(ms)):
            if i == 0:
                res += ms[i]
            elif i < (len(ms)-1) and ms[i].lower() == u'и':
                res += ' ' + ms[i]
            else:
                res += '<br>' + ms[i]

        return res


#recursive_menu
    def get_subtree(lst_str, p_cat, site, level):
        categories = Product.objects.filter(is_category=True).filter(parent_object=p_cat).filter(site=site)
        if categories.count() > 0:
            if (level == 0):
                lst_classes = list_classes
                lst_classes.append('level0')
                classes_str = ' '.join(lst_classes)
                if ul_id == '':
                    lst_str += '<ul class="' + classes_str + '">'
                else:
                    lst_str += '<ul id="' + ul_id + '" class="' + classes_str + '">'
            else:
                lst_str += '<ul class="menu level' + str(level) + '">'
            for category in categories:
                children = Product.objects.filter(parent_object=category).filter(site=site)
                if children.exists():
                    lst_el_classes = list_elements_classes
                    classes_str = ' '.join(lst_el_classes)
                    if children.filter(is_category=True).exists():

                        lst_str += '<li class="level' + str(level) + ' has-children ' + classes_str + '">'
                    else:
                        lst_str += '<li class="level' + str(level) + ' ' + classes_str + '">'
                    lst_str += '<a href="' + lugati_base_url + str(category.id) + '">'
                    if level == 0:
                        lst_str += format_name(category.name)
                    else:
                        lst_str += category.name.strip()
                    lst_str += '</a>'
                    lst_str += get_subtree('', category, site, level+1)
                    lst_str += '</li>'
            lst_str += '</ul>'
        return lst_str
#~recursive_menu

    list_str = get_subtree('', None, cur_site, 0)

    return {
        #'categories': categories,
        'lugati_base_url': lugati_base_url,
        'list_str': list_str
    }

@register.inclusion_tag('lugati_shop/ng_categories_menu.html', takes_context=True)
def lugati_ng_categories_menu(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    lugati_base_url = settings.LUGATI_CATALOG_URL

    #recursive_menu
    def get_subtree(lst_str, p_cat, site, level):
        categories = Product.objects.filter(is_category=True).filter(parent_object=p_cat).filter(site=site)

        if categories.count() > 0:

            lst_str += '<ul class="menu level_' + str(level) + '">'

            for category in categories:
                children = Product.objects.filter(parent_object=category).filter(site=site)
                if children.exists():
                    if children.exists():
                        lst_str += '<li class="level_' + str(level) + ' has-children">'
                    else:
                        lst_str += '<li class="level_' + str(level) + '>'
                    lst_str += '<a href="/catalog/#/catalog/' + str(category.id) + '">'
                    lst_str += category.name.strip()
                    lst_str += '</a>'
                    lst_str += get_subtree('', category, site, level + 1)
                    lst_str += '</li>'
            lst_str += '</ul>'
        return lst_str
    #~recursive_menu

    list_str = get_subtree('', None, cur_site, 0)

    return {
        'lugati_base_url': lugati_base_url,
        'list_str': list_str
    }

@register.inclusion_tag('lugati_shop/catalog/products_list.html', takes_context = True)
def lugati_products_list(context):
    res_dt = {}
    request = context['request']
    cur_site = get_current_site(request)
    lugati_base_url = settings.LUGATI_CATALOG_URL

    cat_id, prod_id = get_ids(request)

    products = None
    if cat_id <> '':
        products = Product.objects.filter(parent_object=cat_id).filter(is_category = False).filter(site=cur_site)
        categories = Product.objects.filter(parent_object=cat_id).filter(is_category = True).filter(site=cur_site)
    else:
        products = Product.objects.filter(parent_object=None).filter(is_category = False).filter(site=cur_site)
        categories = Product.objects.filter(parent_object=None).filter(is_category = True).filter(site=cur_site)


    res_dt['categories'] = []
    for category in categories:
        if Product.objects.filter(parent_object=category).exists():
            res_dt['categories'].append(category)


    if 'brand' in request.GET:
        products = products.filter(brand=Brand.objects.get(pk=request.GET['brand']))

    res_dt['products'] = products


    return res_dt

@register.inclusion_tag('widgets/shop/category_description.html', takes_context=True)
def lugati_category_description(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    #match = resolve(visit.url)

    cat_id, prod_id = get_ids(request)
    category = None
    try:
        category = Product.objects.get(pk=cat_id, site=cur_site)
    except:
        test =1
        #logger.info(str(e))

    return {
        'lugati_base_url': lugati_base_url,
        'category': category
    }

@register.inclusion_tag('widgets/shop/cart_widget/cart_widget.html', takes_context=True)
def lugati_cart_widget(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    cart_items = cart.get_cart_items(request)

    total_sum = 0
    for cart_item in cart_items:
        total_sum += cart_item.product.get_price()

    return {
        'lugati_base_url': lugati_base_url,
        'cart_items': cart_items,
        'total_sum': total_sum
    }

#@register.simple_tag(takes_context=True)
#def lugati_get_cart_items(context):
#    request = context['request']
#    lugati_base_url = request.path
#    cur_site = get_current_site(request)
#
#    from lugati.lugati_shop import cart
#    return cart.get_cart_items(request)

    #return 'fuck'

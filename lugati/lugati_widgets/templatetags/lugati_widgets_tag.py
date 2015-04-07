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
from django.contrib.flatpages.models import FlatPage

register = Library()

@register.inclusion_tag('widgets/plain_text_edit.html', takes_context=True)
def lugati_plain_text_edit(context, flatpage_id):
    request = context['request']
    curSite = get_current_site(request)
    flatPage = FlatPage.objects.get(sites__in=[curSite], url=('/' + flatpage_id +'/'))
    return {
        'request': request,
        'flatPage': flatPage,
        'flatpage_id': flatpage_id
    }

@register.inclusion_tag('widgets/shop/categories.html', takes_context=True)
def lugati_catalog_menu(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    lugati_base_url = settings.LUGATI_CATALOG_URL


    parent_object = None
    if 'parent_product' in request.GET:
        parent_object = Product.objects.get(pk=request.GET['parent_product'], site=cur_site)

    path_list = []
    if parent_object:
        top_level_cat = parent_object
        path_list.append(top_level_cat)
        while True:
            if top_level_cat.parent_object:
                top_level_cat = top_level_cat.parent_object
                path_list.append(top_level_cat)
            else:
                break

#recursive_menu
    def get_subtree(lst_str, p_list, p_cat, site, level):
        categories = Product.objects.filter(is_category=True).filter(parent_object=p_cat).filter(site=site)
        if categories.count() > 0:
            lst_str += '<ul>'
            for category in categories:
                lst_str += '<li class="level_' + str(level) + ' category_item">'
                if category in p_list:
                    lst_str += '<a href="' + lugati_base_url + str(category.id) + '" class="active">'
                    lst_str += category.name
                    lst_str += '</a>'
                    lst_str += get_subtree('', p_list, category, site, level+1)

                else:
                    lst_str += '<a href="' + lugati_base_url + str(category.id) + '">'
                    lst_str += category.name
                    lst_str += '</a>'

                lst_str += '</li>'
            lst_str += '</ul>'
        return lst_str
#~recursive_menu

    list_str = get_subtree('', path_list, None, cur_site, 1)

    categories = Product.objects.filter(is_category=True).filter(parent_object=parent_object).filter(site=cur_site)
    return {
        'categories': categories,
        'lugati_base_url': lugati_base_url,
        'list_str': list_str
    }

@register.inclusion_tag('widgets/shop/categories.html', takes_context=True)
def lugati_catalog_menu_new(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    lugati_base_url = settings.LUGATI_CATALOG_URL


    parent_object = None
    if 'parent_product' in request.GET:
        parent_object = Product.objects.get(pk=request.GET['parent_product'], site=cur_site)

    path_list = []
    if parent_object:
        top_level_cat = parent_object
        path_list.append(top_level_cat)
        while True:
            if top_level_cat.parent_object:
                top_level_cat = top_level_cat.parent_object
                path_list.append(top_level_cat)
            else:
                break

#recursive_menu
    def get_subtree(lst_str, p_list, p_cat, site, level):
        categories = Product.objects.filter(is_category=True).filter(parent_object=p_cat).filter(site=site)
        if categories.count() > 0:
            if (level > 1):
                lst_str += '<ul class="dropdown-menu navmenu-nav">'
            else:
                lst_str += '<ul class="nav navmenu-nav" role="menu">'
            # lst_str += '<ul class="nav nav-pills nav-stacked">'
            for category in categories:
                lst_str += '<li class="level_' + str(level) + ' category_item">'
                # if category in p_list:
                #     lst_str += '<a href="' + lugati_base_url + str(category.id) + '" class="active">'
                #     lst_str += category.name
                #     lst_str += '</a>'
                #     lst_str += get_subtree('', p_list, category, site, level+1)
                # else:
                if (Product.objects.filter(is_category=True).filter(parent_object=category).filter(site=site).count() > 0):
                    lst_str += '<a href="#" class="dropdown-toggle" data-toggle="dropdown">'
                    lst_str += category.name
                    lst_str += '<b class="caret"></b></a>'
                    lst_str += get_subtree('', p_list, category, site, level+1)
                else:
                    lst_str += '<a href="/products?category=' + str(category.id) + '">'
                    lst_str += category.name
                    lst_str += '</a>'

                lst_str += '</li>'
            lst_str += '</ul>'
        return lst_str
#~recursive_menu

    list_str = get_subtree('', path_list, None, cur_site, 1)

    return {
        'lugati_base_url': lugati_base_url,
        'list_str': list_str
    }
@register.inclusion_tag('widgets/shop/product_details.html', takes_context=True)
def lugati_product_details(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    object = Product.objects.get(pk=request.GET['id'])
    return {
        'object': object,
        'request': request
    }
@register.inclusion_tag('widgets/shop/catalog_new.html', takes_context=True)
def lugati_catalog_new(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    # resolve()

    from lugati.lugati_widgets.templatetags.lugati_catalog_wigets_tag import get_ids
    cat_id, prod_id = get_ids(request)

    if cat_id <> '':
        parent_object = Product.objects.get(pk=cat_id)
        products = Product.objects.filter(parent_object=parent_object).filter(site=cur_site).filter(is_category=False)
        # categories = Product.objects.filter(parent_object=parent_object).filter(site=cur_site).filter(is_category=True)
    else:
        products = Product.objects.filter(is_category=False).filter(site=cur_site).filter(pk__in=Bestseller.objects.all().values('product'))
        # categories = []#Product.objects.filter(parent_object=parent_object).filter(site=cur_site).filter(is_category=True)

    #if products.count() == 0:
    #    products = Product.objects.filter(is_category=False).filter(site=cur_site).filter(pk__in=Bestseller.objects.all().values('product'))
    #    categories = True


    return {
        'objects': products,
        'lugati_base_url': lugati_base_url,
        'request': request
    }

@register.inclusion_tag('widgets/shop/cart.html', takes_context=True)
def lugati_cart(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    # resolve()

    return {
        'request': request
    }

@register.inclusion_tag('widgets/shop/catalog.html', takes_context=True)
def lugati_catalog(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    from lugati.lugati_widgets.templatetags.lugati_catalog_wigets_tag import get_ids
    cat_id, prod_id = get_ids(request)

    if cat_id <> '':
        parent_object = Product.objects.get(pk=cat_id)
        products = Product.objects.filter(parent_object=parent_object).filter(site=cur_site).filter(is_category=False)
        categories = Product.objects.filter(parent_object=parent_object).filter(site=cur_site).filter(is_category=True)
    else:
        products = Product.objects.filter(is_category=False).filter(site=cur_site).filter(pk__in=Bestseller.objects.all().values('product'))
        categories = []#Product.objects.filter(parent_object=parent_object).filter(site=cur_site).filter(is_category=True)

    #if products.count() == 0:
    #    products = Product.objects.filter(is_category=False).filter(site=cur_site).filter(pk__in=Bestseller.objects.all().values('product'))
    #    categories = True


    return {
        'categories': categories,
        'products': products,
        'lugati_base_url': lugati_base_url
    }

@register.inclusion_tag('widgets/slider.html', takes_context=True)
def lugati_slider(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    #img_folder = settings.MEDIA_ROOT + 'custom/' + cur_site.name + '/img/slider/'
    #img_path = settings.MEDIA_URL + 'custom/' + cur_site.name + '/img/slider/'
    #
    slider_images = []
    #for slider_img in os.listdir(img_folder):
    #    slider_images.append({
    #        'src': img_path + slider_img,
    #        'link': '#'
    #    })
    for slider_item in SliderItem.objects.filter(site=cur_site):
        if slider_item.get_images().count() > 0:
            slider_images.append({
                'src': slider_item.get_images()[0].file.url,
                'link': slider_item.link
            })


    return {
        'lugati_base_url': lugati_base_url,
        'slider_images': slider_images
    }

@register.inclusion_tag('widgets/shop/special_offer.html', takes_context=True)
def lugati_special_offer(context):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    products_special = SpecialOffer.objects.all()[:3]

    return {
        'lugati_base_url': lugati_base_url,
        'special_offer': products_special
    }

@register.inclusion_tag('widgets/text_block.html', takes_context=True)
def lugati_text_block(context, block_id):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)
    try:
        text_block = LugatiTextBlock.objects.get(pk=block_id)
    except:
        text_block = None
    return {
        'text_block': text_block
    }

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

@register.assignment_tag(takes_context=True)
def get_lugati_objects(context, content_type_id, is_category=None, parent_object=None):
    request = context['request']
    lugati_base_url = request.path
    cur_site = get_current_site(request)

    model_class = ContentType.objects.get(pk=content_type_id).model_class()
    objects = model_class.objects.all()

    if hasattr(model_class, 'site'):
        objects = objects.filter(site=cur_site)

    if hasattr(model_class, 'parent_object'):
        objects = objects.filter(parent_object=parent_object)
        if is_category <> None:
            try:
                objects = objects.filter(is_category=is_category)
            except Exception, e:
                pass
    return objects



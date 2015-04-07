# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from .models import Product, ProductPrice, Bestseller
from .forms import ProductForm, CategoryForm, ToppingForm
from django.conf import settings
from django.contrib.sites.models import get_current_site
import json
from lugati.lugati_media.models import ThebloqImage
from rest_framework.renderers import JSONRenderer
from lugati.products.models import Brand
from lugati.lugati_registration.models import LugatiUserProfile
from django.core.urlresolvers import resolve
from lugati.lugati_shop.models import ShoppingPlace
from lugati.lugati_shop.models import LugatiCompany

import logging
import lugati.lugati_shop.cart as cart
from django.contrib.contenttypes.models import ContentType
logger = logging.getLogger(__name__)

#API
#deprecated
def get_products(request):
    res_dt = {}
    return HttpResponse(json.dumps(res_dt))
#deprecated
def api_brands(request, id=''):
    cur_site = get_current_site(request)
    brands = Brand.objects.filter(site=cur_site).order_by('name')
    if 'cur_cat' in request.GET:
        cur_cat = request.GET['cur_cat']
        brands = brands.filter(pk__in=set(Product.objects.filter(site=cur_site).filter(parent_object=cur_cat).values_list('brand', flat=True).distinct())).order_by('name')
    res_dt = []
    for brand in brands:
        node = {
            'id': brand.id,
            'name': brand.name
        }
        res_dt.append(node)
    return HttpResponse(json.dumps(res_dt))


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def api_products(request, id='', brand_id=''):
    res_dt = {}
    cur_site = get_current_site(request)
    if request.method == 'PUT':
        product_dt = json.loads(request.body)
        product_dt['site'] = cur_site.id
        if 'parent_object' not in product_dt:
            product_dt['parent_object'] = None
        if product_dt['is_category'] == 'True':
            form = CategoryForm(request=request, instance=Product.objects.get(pk=id), data=product_dt)
            form.save()

        else:
            form = ProductForm(request=request, instance=Product.objects.get(pk=id), data=product_dt)
            form.save()

        return HttpResponse(json.dumps(res_dt))
    else:
        if id == '':
            #new one or update
            if request.method == 'POST':
                product_dt = json.loads(request.body)
                if not 'site' in product_dt:
                    product_dt['site'] = cur_site.id
                product_dt['company'] = LugatiUserProfile.objects.get(user=request.user).get_company().id
                # product_dt['price_wo_discount'] = 0

                if (product_dt['is_category'] == 'True') or (product_dt['is_category'] == True):

                    form = CategoryForm(request=request, data=product_dt)
                    #if form.is_valid():
                    logger.info('err: ' + str(form._errors))
                    try:
                        obj = form.save()
                        ms = form.cleaned_data['pic_array'].split(';')
                        for img_id in ms:
                            if str(img_id).strip() <> '':
                                tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                                tb_image.content_object = obj
                                tb_image.save()
                    except Exception, e:
                        logger.info('err: ' + str(form._errors))

                else:
                    if 'price' in product_dt:
                        if not product_dt['price']:
                            product_dt['price'] = 0
                    else:
                        product_dt['price'] = 0

                    if 'is_topping' in product_dt:
                        if product_dt['is_topping']:
                            # from django.contrib.sites.models import Site
                            form = ToppingForm(request=request, data=product_dt)
                            obj = Product()
                            obj.company = LugatiCompany.objects.get(pk=product_dt['company'])
                            obj.site = cur_site
                            obj.is_category = product_dt['is_category']
                            obj.is_topping = product_dt['is_topping']
                            obj.price = product_dt['price']
                            obj.name = product_dt['name']
                            obj.styled_name = product_dt['name']
                            obj.parent_object = Product.objects.get(pk=product_dt['parent_object'])
                            obj.save()
                            return HttpResponse(json.dumps(obj.get_list_item_info(request)))

                    form = ProductForm(request=request, data=product_dt)
                    obj = form.save()
                    ms = form.cleaned_data['pic_array'].split(';')
                    for img_id in ms:
                        if str(img_id).strip() <> '':
                            tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                            tb_image.content_object = obj
                            tb_image.save()

                return HttpResponse(json.dumps(obj.get_list_item_info(request)))

            #query for products
            if request.method == 'GET':

                parent_object = None

                products = Product.objects.filter(site=cur_site)

                #filter
                if settings.LUGATI_SPLIT_CATALOG_BY_COMPANY:
                    if request.user.is_authenticated():
                        cur_profile = LugatiUserProfile.objects.get(user=request.user)
                        products = products.filter(company=cur_profile.get_company())
                    else:
                        try:
                            match = resolve(request.GET['cur_path'])
                            pos_id = match.kwargs['pos_id']
                            cur_company = ShoppingPlace.objects.get(pk=pos_id).shop.company
                            products = products.filter(company=cur_company)
                        except Exception, e:
                            products = products.filter(company=None)
                            pass


                #deprecated!!!
                if 'parent_product' in request.GET:
                    parent_object = request.GET['parent_product']
                #~deprecated!!!
                elif 'parent_object' in request.GET:
                    parent_object = request.GET['parent_object']
                elif 'cat_id' in request.GET:
                    parent_object = request.GET['cat_id']


                if 'obj_type' in request.GET:
                    if request.GET['obj_type'] == 'topping':
                        products = products.filter(is_category=False).filter(is_topping=True)
                        if not request.user.is_authenticated():
                            products = products.filter(assigned_to__in=[request.GET['assigned_to_id']])
                        if 'assigning' in request.GET:
                            if request.GET['assigning']:
                                products = products.filter(parent_object=Product.objects.get(pk=request.GET['parent_id']))
                        # else:
                        #
                    else:
                        products = products.filter(is_topping=False)
                else:
                    products = products.filter(is_topping=False)
                    products = products.filter(parent_object=parent_object)

                if (brand_id <> ''):
                    products = products.filter(brand=Brand.objects.get(pk=brand_id))
                elif ('brand_id' in request.GET):
                    products = products.filter(brand=Brand.objects.get(pk=request.GET['brand_id']))

                #~filter



                res_dt = []
                cur_num = 1
                for product in products:
                    if settings.SHOP_TYPE=='MPS':
                        if product.styled_name.strip() == '':
                            product.delete()
                            continue

                    node = product.get_list_item_info(request)
                    if not product.is_category:
                        node['num'] = cur_num
                        cur_num += 1
                    else:
                        node['number_of_items'] = Product.objects.filter(parent_object=product).count()

                    res_dt.append(node)

            return HttpResponse(json.dumps(res_dt))
#single product
        else:
            if request.method == 'GET':
                product = Product.objects.get(pk=id)
                res_dt = product.get_list_item_info(request)
            return HttpResponse(json.dumps(res_dt))
    #~API

#manage products
def manage_products(request):
    resp_data = {}
    return render(request, 'products/manage/manage_products.html', resp_data)

# def manage_products_ajax_new(request):
#     cur_site = get_current_site(request)
#     #cat_id = request.GET['cat_id']
#     #res_dt = []
#     def get_products_tree(parent_object=None, level=0):
#         dt = []
#         products = Product.objects.filter(site=cur_site).filter(parent_object=parent_object).order_by('is_category', 'priority')
#         for product in products:
#             cur_node = {
#                 'label': product.name,
#                 'uid': product.id,
#                 'data': {
#                     'definition': product.preview
#                 }
#             }
#             children = Product.objects.filter(parent_object=product)
#             if children.exists():
#                 cur_node['children'] = get_products_tree(parent_object=product, level=level+1)
#             dt.append(cur_node)
#         return dt
#
#     res_dt = get_products_tree()
#
#
#     return HttpResponse(json.dumps(res_dt))

def delete_thumbnail(request, product_id):
    product = Product.objects.get(pk=product_id)
    thum = product.thumbnail
    product.thumbnail = None
    product.save()
    if thum:
        thum.delete()
    imgs = product.get_images()
    for img in imgs:
        img.delete()
    return HttpResponse(json.dumps({}))

#~manage products

def product_page(request, pr_id):
    product = Product.objects.get(id=pr_id)
    resp_data = {}
    resp_data['product'] = product
    return render(request, 'products/product_page.html', resp_data)

# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from lugati.products.models import Product, Brand

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from lugati.lugati_mobile.models import LugatiDevice
import datetime
from gcm.gcm import GCM
from . import cart
from lugati.lugati_shop.lugati_orders.models import Order, OrderItem, OrderItemOption
from lugati.lugati_shop.lugati_cart.models import CartItemOption
from django.template import Context
from .forms import CofirmOrderForm
from django.shortcuts import redirect
from django.template.loader import get_template
import json

import logging
from django.contrib.sites.models import get_current_site
from django.http import Http404
from django.core.urlresolvers import resolve
from twilio.rest import TwilioRestClient
from lugati.lugati_shop.models import PhoneNumber
from sorl.thumbnail.images import ImageFile, DummyImageFile
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry
from sorl.thumbnail import get_thumbnail
from django.views.decorators.csrf import csrf_exempt
import decimal

from lugati.lugati_shop.lugati_delivery.models import DeliveryOption, City
from lugati.lugati_shop.models import ShoppingPlace, Shop, LugatiClerk, LugatiCompany, LugatiShoppingSession

from lugati.lugati_shop.lugati_orders.models import OrderState
from lugati.lugati_media.models import ThebloqImage
from lugati.lugati_registration.models import LugatiUserProfile
from django.template import Context, Template
from django.conf import settings

import cStringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from cgi import escape
import stomp

import requests
logger = logging.getLogger(__name__)

if settings.HAS_TWILIO:
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

gcm = GCM(settings.GCM_APIKEY)

stomp_conn = stomp.Connection()
stomp_conn.start()
stomp_conn.connect()

def clear_cart(request):
    items = cart.get_cart_items(request)
    for item in items:
        item.delete()
    return HttpResponse()

def single_order_point_qr_code(request, object_id=''):
    order_point = ShoppingPlace.objects.get(pk=object_id)
    res_dt = {
        'object': order_point
    }
    template = get_template('lugati_admin/lugati_version_1_0/order_points/single_order_point_qr_code.html')
    context = Context(res_dt)
    html = template.render(context)
    headers = {'content-type': 'application/json'}
    resp = requests.post('http://127.0.0.1:8899', data=json.dumps({'html_txt': html}), headers=headers)
    res_dt['tb_img'] = ThebloqImage.objects.get(pk=resp.json()['id'])
    return HttpResponse(res_dt['tb_img'].file, content_type="image/png")
    # return render(request, 'lugati_admin/lugati_version_1_0/order_points/single_order_point_qr_code.html', res_dt)

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)

    html = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')

    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def pdf_order_points_stickers(request, col_num=''):
    resp_dt = {}
    order_points = ShoppingPlace.objects.filter(
        shop__in=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company()))

    resp_dt['rows'] = []
    col_num = int(col_num)
    ind = 0

    for order_point in order_points:
        if ind % col_num == 0:
            resp_dt['rows'].append([])
        node = order_point.get_list_item_info()
        res_dt = {
            'object': order_point
        }
        template = get_template('lugati_admin/lugati_version_1_0/order_points/single_order_point_qr_code.html')
        context = Context(res_dt)
        html = template.render(context)
        headers = {'content-type': 'application/json'}
        resp = requests.post('http://127.0.0.1:8899', data=json.dumps({'html_txt': html}), headers=headers)
        node['tb_img'] = ThebloqImage.objects.get(pk=resp.json()['id'])
        node['cur_server'] = order_point.get_cur_server()
        resp_dt['rows'][len(resp_dt['rows']) - 1].append(node)

        ind += 1
    if ind < col_num:
        resp_dt['rows'][len(resp_dt['rows']) - 1].append({})
    resp_dt['pagesize'] = 'A4'
    # return render(request, 'lugati_admin/lugati_version_1_0/include/order_points/generate_order_points_wrapper.html', resp_dt)
    return render_to_pdf(
        'lugati_admin/lugati_version_1_0/include/order_points/generate_order_points_wrapper.html',
        resp_dt
    )

def generate_order_points_stickers(request, object_id=''):
    resp_dt = {}
    order_points = ShoppingPlace.objects.filter(
        shop__in=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company()))
    if object_id <> '':
        order_points.filter(pk=object_id)
    col_num = 2
    resp_dt['rows'] = []
    ind = 0

    for order_point in order_points:
        if ind % col_num == 0:
            resp_dt['rows'].append([])
        resp_dt['rows'][len(resp_dt['rows']) - 1].append(order_point.get_list_item_info())
        ind += 1

    return render(request, 'lugati_admin/lugati_version_1_0/include/order_points/generate_order_points.html', resp_dt)


def send_tracking_number(request):
    cur_site = get_current_site(request)
    order_id = request.GET['order_id']
    tracking_number = request.GET['tracking_number']
    order = Order.objects.get(pk=order_id)
    logger.info('trying to send tracking number')
    try:
        t = get_template('custom/' + cur_site.name + '/catalog/tracking_template.html')
        message_html = t.render(Context({'order_id': order.id,
                                         'paid': True,
                                         'tracking_number': tracking_number,
                                         'cart_items': OrderItem.objects.filter(order=order),
                                         'mail': True,
                                         'email': order.email,
                                         'phone': order.phone,
                                         'address': order.address,
                                         'name': order.name,
                                         'dt_add': order.dt_add,
                                         'shop_name': cur_site.name,
                                         'delivery_price': order.delivery_price,
                                         'total': decimal.Decimal(order.get_total_sum()) + decimal.Decimal(
                                             order.delivery_price)}))

    except Exception, e:
        logger.info(str(e))
        t = get_template('lugati_shop/order_mail.html')
        message_html = t.render(Context({'order_id': order.id,
                                         'paid': True,
                                         'tracking_number': tracking_number,
                                         'cart_items': OrderItem.objects.filter(order=order),
                                         'mail': True,
                                         'email': order.email,
                                         'phone': order.phone,
                                         'address': order.address,
                                         'name': order.name,
                                         'shop_name': cur_site.name,
                                         'delivery_price': order.delivery_price,
                                         'total': decimal.Decimal(order.get_total_sum()) + decimal.Decimal(
                                             order.delivery_price)}))

    subject = str(cur_site.domain) + ': Ваш заказ № ' + str(order.id)
    emails = [order.email, 'tracking@sola-monova.com']
    try:
        msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
        msg.attach_alternative(message_html, "text/html")
        msg.send()
    except Exception, e:
        logger.error(str(e))
    return HttpResponse(json.dumps({}))


def load_demo_data(request):
    # from lugati.products.products_procs import create_demo_account
    # from django.conf import settings

    prof = LugatiUserProfile.objects.get(user=request.user)
    Order.objects.filter(shopping_place__in=ShoppingPlace.objects.filter(
        shop__in=Shop.objects.filter(company=prof.get_company()))).delete()
    Product.objects.filter(company=prof.get_company()).delete()
    ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=prof.get_company())).delete()

    # generate_order_points(site_id, user)
    # load_demo_data(site_id, user)
    # generate_week_sales(site_id, user)

    # create_demo_account(settings.SITE_ID, LugatiUserProfile.objects.get(user=request.user))
    return HttpResponse(json.dumps({}))


def generate_demo_order_points(request):
    from lugati.products.products_procs import generate_order_points

    generate_order_points(settings.SITE_ID, request.user)
    return HttpResponse(json.dumps({}))


def generate_demo_inventory(request):
    from lugati.products.products_procs import load_demo_data

    load_demo_data(settings.SITE_ID, request.user)
    return HttpResponse(json.dumps({}))


def generate_demo_sales(request):
    from lugati.products.products_procs import generate_week_sales

    generate_week_sales(settings.SITE_ID, request.user)
    return HttpResponse(json.dumps({}))


def generate_order_points(request):
    from lugati.products.products_procs import generate_order_points

    amount_of_tables = request.GET['amount_of_tables']
    generate_order_points(settings.SITE_ID, request.user, int(amount_of_tables))
    return HttpResponse(json.dumps({}))


def change_company_data(request):
    company_name = request.GET['company_name']
    prof = LugatiUserProfile.objects.get(user=request.user)
    company = prof.get_company()
    company.name = company_name
    company.save()
    return HttpResponse(json.dumps({}))


def ng_crop_image_template(request, content_object_id, object_id, image_id):
    resp_data = {}
    resp_data['mps_image'] = ThebloqImage.objects.get(pk=image_id)
    return render(request, 'custom/mps/ng_crop_image_template.html', resp_data)


def clerk_login(request):
    dt = request.GET
    res_dt = {}

    try:
        clerk = LugatiClerk.objects.get(login=dt['login'], password=dt['password'],
                                        company=LugatiCompany.objects.get(pk=dt['company_id']))

        dev_id = dt['dev_id']
        reg_id = dt['reg_id']

        device = None
        if LugatiDevice.objects.filter(dev_id=dev_id).exists():
            device = LugatiDevice.objects.filter(dev_id=dev_id)[0]
        else:
            device = LugatiDevice()
            device.dev_id = dev_id
            device.reg_id = reg_id
            device.name = dev_id
            device.save()
        clerk.device = device
        clerk.save()
        res_dt['msg'] = 'success'
    except Exception, e:
        res_dt['msg'] = 'fail'

    return HttpResponse(json.dumps(res_dt))


def lugati_call(request):
    return HttpResponse(json.dumps({}))


def get_ng_cart_template(request):
    current_site = get_current_site(request)
    cur_site_name = current_site.name

    resp_data = {
        'cur_site_name': cur_site_name
    }

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'ng_cart.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)
        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


def get_ng_product_details_template(request):
    current_site = get_current_site(request)
    cur_site_name = current_site.name

    resp_data = {
        'cur_site_name': cur_site_name
    }

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'ng_product_details.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)
        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


def get_ng_catalog_template(request):
    current_site = get_current_site(request)
    cur_site_name = current_site.name

    resp_data = {
        'cur_site_name': cur_site_name
    }

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'ng_catalog.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)
        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


@csrf_exempt
def get_cart_items(request):
    cur_site = get_current_site(request)

    thumbnail_size_str = '110x110'
    res_dt = {
        'cart_items': [],
        'total_price': 0,
        'total_quantity': 0,
        'total_delivery_price': 0,
    }

    items = cart.get_cart_items(request)
    for item in items:

        cur_item = {
            'id': item.product.id,
            'sku': item.product.sku,
            'name': item.product.name,
            'price': str(item.product.get_price()).rstrip('0').rstrip('.'),
            'quantity': item.quantity,
            'total': str(item.total()).rstrip('0').rstrip('.')
        }

        try:
            image_tmb = get_thumbnail(item.product.get_main_image().file, thumbnail_size_str, quality=100)
        except:
            image_tmb = None

        if image_tmb:
            cur_item['product_url'] = '/catalog/product_details/' + str(item.product.id)
            cur_item['main_image_url'] = item.product.get_main_image().file.url
            cur_item['image_url'], cur_item['image_margin'] = item.product.get_main_image().get_thumbnail_attributes(
                item.product.get_main_image().get_thumbnail(thumbnail_size_str), thumbnail_size_str)

        else:
            cur_item['product_url'] = '/catalog/product_details/' + str(item.product.id)
            cur_item['main_image_url'] = ''
            cur_item['image_url'] = ''
            cur_item['image_margin'] = ''

        res_dt['cart_items'].append(cur_item)
        res_dt['total_price'] += (item.total())
        res_dt['total_quantity'] += item.quantity



    # todo delivery
    delivery_cart_options = cart.get_all_cart_delivery(request)
    if delivery_cart_options.exists():
        total_delivery_cost = decimal.Decimal(0)
        total_delivery_additional_cost = decimal.Decimal(0)
        for delivery_cart_option in delivery_cart_options:
            total_delivery_cost += delivery_cart_option.delivery_option.price
            total_delivery_additional_cost += delivery_cart_option.delivery_option.additional_price
        total_quantity = res_dt['total_quantity']
        try:
            res_dt['total_delivery_price'] = float(total_delivery_cost) + float(
                ((total_quantity - 1) * total_delivery_additional_cost))
        except Exception, e:
            logger.info(str(e))
    else:
        delivery_options = DeliveryOption.objects.filter(site=cur_site)
        if delivery_options.exists():
            res_dt['total_delivery_price'] = float(delivery_options[0].price)
    # ~todo delivery
    res_dt['total_price_wo_delivery'] = str(res_dt['total_price']).rstrip('0').rstrip('.')
    res_dt['total_price'] = str(res_dt['total_price'] + decimal.Decimal(res_dt['total_delivery_price'])).rstrip(
        '0').rstrip('.')

    return HttpResponse(json.dumps(res_dt))


@csrf_exempt
def shopping_cart(request):
    current_site = get_current_site(request)
    cur_site_name = current_site.name
    resp_data = {
        'cur_site_name': cur_site_name
    }

    cart_items = cart.get_cart_items(request)

    total_sum = 0
    for cart_item in cart_items:
        total_sum += cart_item.product.get_price()

    resp_data['total_sum'] = total_sum
    resp_data['cart_items'] = cart_items

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'cart.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)

        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


@csrf_exempt
def pos_catalog(request, pos_id='', cat_id=''):
    current_site = get_current_site(request)
    cur_site_name = current_site.name
    cur_shopping_place = ShoppingPlace.objects.get(pk=pos_id)
    resp_data = {
        'cur_site_name': cur_site_name,
        'debug': settings.DEBUG
    }

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'catalog.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)

        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


@csrf_exempt
def pos_catalog_start(request, pos_id='', cat_id=''):
    current_site = get_current_site(request)
    cur_site_name = current_site.name
    cur_shopping_place = ShoppingPlace.objects.get(pk=pos_id)

    resp_data = {
        'cur_site_name': cur_site_name,
        'menu_path': settings.POS_SERVER + '/catalog/point_of_sale/' + pos_id + '/#/mps_catalog/'
    }

    # sets = ShopSetting.objects.filter(shop=cur_shopping_place.shop)
    # if sets.count() > 0:
    # if ShopSetting.objects.get(shop=cur_shopping_place.shop).logo_img:
    # resp_data['logo_path'] = ShopSetting.objects.get(shop=cur_shopping_place.shop).logo_img.file.url
    #     else:
    #         resp_data['logo_path'] = '/media/custom/mps/img/lugati_default/default_logo.png'
    # else:
    #     resp_data['logo_path'] = '/media/custom/mps/img/lugati_default/default_logo.png'
    resp_data['logo_path'] = cur_shopping_place.shop.get_logo().file.url

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'catalog_start.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)

        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


def catalog(request, cat_id='', prod_id=''):
    current_site = get_current_site(request)
    cur_site_name = current_site.name
    resp_data = {
        'cur_site_name': cur_site_name
    }

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'catalog.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)

        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


@csrf_exempt
def product_details(request, prod_id=''):
    current_site = get_current_site(request)
    cur_site_name = current_site.name
    resp_data = {
        'cur_site_name': cur_site_name
    }

    catalog_template_dir = 'catalog'
    template_name = catalog_template_dir + '/' + 'product_details.html'

    if not settings.DEBUG:
        try:
            return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)

        except:
            raise Http404
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)


@csrf_exempt
def add_product_to_cart(request):
    quantity = int(request.POST['quantity'])
    prod_id = int(request.POST['prod_id'])
    cur_cart_item = None

    if quantity >= 0:
        cur_cart_item = cart.add_product_to_cart(request)
    else:
        cur_cart_item = cart.remove_product_from_cart(request)

    product = Product.objects.get(id=prod_id)
    res = [product.name, product.get_price_str()]

    t = get_template('widgets/shop/cart_widget/cart_widget_content.html')

    cart_items = cart.get_cart_items(request)
    total_sum = 0
    for cart_item in cart_items:
        total_sum += cart_item.total()

    cart_widget_content = t.render(Context({
        'cart_items': cart_items,
        'total_sum': total_sum
    }))

    return HttpResponse(json.dumps({
        'result': res,
        'id': prod_id,
        'product_name': product.name,
        'cart_widget_content': cart_widget_content
    }))


@csrf_exempt
def remove_product_from_cart(request):
    cart.remove_product_from_cart(request)
    cur_site = get_current_site(request)

    t = get_template('widgets/shop/cart_widget/cart_widget_content.html')

    cart_items = cart.get_cart_items(request)
    total_sum = 0
    for cart_item in cart_items:
        total_sum += cart_item.total()

    cart_widget_content = t.render(Context({
        'cart_items': cart_items,
        'total_sum': total_sum
    }))

    resp_dt = {
        'cart_widget_content': cart_widget_content,
    }

    match = resolve(request.POST['cur_url'])
    if (match.url_name == 'lugati_shopping_cart'):
        t = get_template('custom/' + cur_site.name + '/catalog/cart_dynamic_content.html')
        resp_dt['cart_content'] = t.render(Context({
            'cart_items': cart_items,
            'total_sum': total_sum
        }))

    return HttpResponse(json.dumps(resp_dt))


# deprecated
def add_product(request):
    prod_id = cart.add_to_cart(request)
    product = Product.objects.get(id=prod_id)
    res = [product.name, product.get_price_str()]
    return render(request, 'lugati_shop/cart/add.html', {'result': res, 'id': request.GET['productId']})


def remove_product(request):
    logger.info(request.GET['productIdToRemove'])
    cart.remove_from_cart(request)
    return HttpResponse("OK")


# ~deprecated
@csrf_exempt
def confirm_order(request):
    logger.info('submit order!!!!')
    cur_site = get_current_site(request)
    cart_items = cart.get_cart_items(request)
    form = CofirmOrderForm(request.POST)
    if form.is_valid():

        order = Order()
        order.site = cur_site
        order.state = OrderState.objects.get(pk=1)
        order.save()

        message_text = u'заказ № ' + str(order.id) + '\n\n'
        message_text += u'Телефон: ' + form.cleaned_data['phone'] + '\n'
        message_text += u'E-mail: ' + form.cleaned_data['mail'] + '\n'
        message_text += u'Адрес доставки: ' + form.cleaned_data['address'] + '\n'

        message_text += u'Уважаемый ' + form.cleaned_data[
            'name'] + u' !\n\nВы оформили заказ в нашем интернет-магазине.'
        message_text += u'Вы заказали следующие товары:'

        #todo delivery
        delivery_options = DeliveryOption.objects.filter(site=cur_site)
        delivery_price = 0
        if delivery_options.exists():
            delivery_price = delivery_options[0].price


        #todo delivery made for sola
        total_quantity = 0
        for item in cart_items:
            total_quantity += item.quantity

        logger.info("delivery: 1")

        del_option = None

        delivery_cart_options = cart.get_all_cart_delivery(request)
        delivery_price = cart.get_total_delivery_price(request)
        online_payment = True
        del_var = 1
        ind = 1
        if delivery_cart_options.exists():
            # logger.info("delivery: 2")
            # total_delivery_cost = decimal.Decimal(0)
            # total_delivery_additional_cost = decimal.Decimal(0)
            for delivery_cart_option in delivery_cart_options:
                del_option = delivery_cart_option.delivery_option
                # logger.info('del_option: ' + str(ind) + ' ' + str(del_option))
                # logger.info("delivery: 3")
                # total_delivery_cost += delivery_cart_option.delivery_option.price
                # total_delivery_additional_cost += delivery_cart_option.delivery_option.additional_price
                online_payment = delivery_cart_option.delivery_option.online_payment
                del_var = delivery_cart_option.delivery_option.del_opt
                ind = ind + 1
            try:
                logger.info("delivery: 4")
                # delivery_price = float(total_delivery_cost) + float(
                #     ((total_quantity - 1) * total_delivery_additional_cost))
            except Exception, e:
                logger.info("delivery: 5")
                logger.info(str(e))
        else:
            logger.info("delivery: 6")
            # delivery_options = DeliveryOption.objects.filter(site=cur_site)
            # if delivery_options.exists():
            #     delivery_price = float(delivery_options[0].price)

        order.delivery_price = delivery_price
        order.save()

        way_var = u'РОБОКАССА'
        if del_var == 1:
            way_var = u'ОПЛАТА ONLINE'
        elif del_var == 2:
            way_var = u'НАЛОЖЕННЫЙ ПЛАТЕЖ'
        elif del_var == 4:
            way_var = u'САМОВЫВОЗ'
        else:
            way_var = u'ОПЛАТА ПРИ ПОЛУЧЕНИИ'
        #~todo delivery

        logger.info('smb2')

        total = decimal.Decimal(0)

        for item in cart_items:
            total += decimal.Decimal(item.total())

        total += decimal.Decimal(delivery_price)

        try:
            logger.info('smb3')
            cur_context = {'order_id': order.id,
                           'cart_items': cart_items,
                           'mail': True,
                           'email': form.cleaned_data['mail'],
                           'phone': form.cleaned_data['phone'],
                           'address': form.cleaned_data['address'],
                           'city': form.cleaned_data['city'],
                           'zip_code': form.cleaned_data['zip_code'],
                           'name': form.cleaned_data['name'],
                           'shop_name': cur_site.name,
                           'delivery_price': delivery_price,
                           'total': total,
                           'payment_method': way_var,
                           'del_var': del_var,
                           'request': request}

            header_text = ''

            logger.info('del_option: ' + str(del_option))
            if del_option:
                try:
                    header_t = Template(del_option.mail_text.replace('{$', '{{').replace('$}', '}}'))
                    header_text = header_t.render(Context(cur_context))
                except Exception, e:
                    logger.info('submit_err: ' + str(e))
            logger.info('header text: ' + header_text)
            cur_context['header_text'] = header_text
            t = get_template('custom/' + cur_site.name + '/catalog/mail_template.html')
            message_html = t.render(Context(cur_context))
            logger.info('smb4')

        except Exception, e:
            import traceback
            #traceback.print_exc()
            traceback.print_exc(file=open('/home/xors/res_trace.txt', 'a'))
            logger.info('smb5')
            logger.info(str(e))
            t = get_template('lugati_shop/order_mail.html')
            message_html = t.render(Context({'order_id': order.id,
                                             'cart_items': cart_items,
                                             'mail': True,
                                             'email': form.cleaned_data['mail'],
                                             'phone': form.cleaned_data['phone'],
                                             'address': form.cleaned_data['address'],
                                             'name': form.cleaned_data['name'],
                                             'shop_name': cur_site.name,
                                             'delivery_price': delivery_price,
                                             'total': total}))
            logger.info('smb6')

        try:
            order.email = form.cleaned_data['mail']
            order.phone = form.cleaned_data['phone']
            order.address = form.cleaned_data['address']
            order.name = form.cleaned_data['name']
            order.delivery_option = DeliveryOption.objects.get(pk=form.cleaned_data['sola_delivery_option'])
            order.city = form.cleaned_data['city']
            order.zip_code = form.cleaned_data['zip_code']
            order.save()
        except Exception, e:
            logger.info(str(e))

#todo for sola
        hasTickets = False
        for cart_item in cart_items:
            order_item = OrderItem()
            order_item.order = order
            order_item.price = cart_item.product.get_price()
            order_item.quantity = cart_item.quantity
            order_item.product = cart_item.product
            order_item.save()
#todo !!! for sola
            try:
                if order_item.product.parent_object:
                    if order_item.product.parent_object.name.lower() == u'билеты':
                        hasTickets = True
            except Exception, e:
                logger.info(str(e))

            cart_item.delete()

            message_text += unicode(
                unicode(order_item.product.name) + ' ' + unicode(str(order_item.quantity)) + ' ' + unicode(
                    order_item.product.get_price_str()) + '\n')

        #todo delivery
        if delivery_price > 0:
            message_text += '\n\n' + unicode(unicode(u'Доставка:') + ' ' + unicode(delivery_price) + '\n')
        #~todo delivery
        message_text += '\n\n' + unicode(unicode(u'Итого:') + ' ' + unicode(total) + '\n')
        subject = str(cur_site.domain) + ': Ваш заказ № ' + str(order.id)
        emails = [form.cleaned_data['mail']]

        #todo!!!
        if (not 'LUGATI_PAYMENT' in settings.LUGATI_MODULES) or (not online_payment):
            try:
                msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
                #msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, emails)
                msg.attach_alternative(message_html, "text/html")
                msg.send()
            except Exception, e:
                logger.error(str(e))
            #to us
            if (hasTickets):
                emails = [settings.DEFAULT_TICKETS_EMAIL]
            else:
                emails = [settings.DEFAULT_FROM_EMAIL]
            try:
                msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, emails)
                msg.attach_alternative(message_html, "text/html")
                msg.send()
            except Exception, e:
                logger.error(str(e))

            for phone_number in PhoneNumber.objects.filter(site=cur_site):
                if settings.HAS_TWILIO:
                    try:
                        message = client.sms.messages.create(body=(unicode(u'новый заказ в магазине ') + cur_site.name),
                                                             to=(phone_number.number),  # Replace with your phone number
                                                             from_=settings.TWILIO_PHONE_NUMBER)  # Replace with your Twilio number

                    except Exception, e:
                        logger.error(str(e))

        return HttpResponse(json.dumps(
            {'response': "Email with a confirmation link has been sent", 'result': 'success', 'order_id': order.id}))
    else:
        response = {}
        for k in form.errors:
            response[k] = form.errors[k][0]
        return HttpResponse(json.dumps({'response': response, 'result': 'error'}))


#API



def lugati_get_payment_template(request):
    res_dt = {}
    if settings.DEBUG:
        res_dt['lugati_debug'] = True

    return render(request, 'lugati_shop/mobile/mobile_payment.html', res_dt)


def lugati_test_pay(request):

    res_dt = {}
    res_dt['test'] = 'test'
    cur_site = get_current_site(request)
    # cart_items = cart.get_cart_items(request)
    cart_id = cart._cart_id(request)

    logger.info('trying body')

    try:
        # sum = 0
        #
        # for cart_item in cart_items:
        #     sum += cart_item.total()
        # logger.info('total sum -> ' + str(sum))
        # if cart_items.count() > 0:
        #     order = Order()
        #     order.site = cur_site
        #     #todo !!!!!
        #     order.cart_id = cart_items[0].cart_id
        #     order.shopping_place = cart_items[0].shopping_place
        #     #~!!!!!
        #     order.save()
        #
        #     for cart_item in cart_items:
        #         order_item = OrderItem()
        #         order_item.order = order
        #         order_item.quantity = cart_item.quantity
        #         order_item.product = cart_item.product
        #         order_item.price = cart_item.get_price()#!!!!
        #         order_item.save()
        #         # copy it to payment
        #         for cart_item_option in CartItemOption.objects.filter(cart_item=cart_item):
        #             order_item_option = OrderItemOption()
        #             order_item_option.order_item = order_item
        #             order_item_option.product_option = cart_item_option.product_option
        #             order_item_option.save()
        #         # ~copy it to payment
        #
        #         logger.info('added -> ' + cart_item.product.name + ' ' + str(cart_item.quantity))
        #         cart_item.delete()
        order = cart.make_order_paid(cart_id)
        if order:
            logger.info('devices' + '1')
            clerks = LugatiClerk.objects.filter(company=order.shopping_place.shop.company)
            for clerk in clerks:
                try:
                    logger.info('trying sending notification')
                    data = {
                        'title': order.shopping_place.shop.company.name,
                        'message': "order " + str(order.id) + " paid (" + str(order.shopping_place) + ")",
                        'timeStamp': datetime.datetime.now().isoformat(),
                        'type': 'new_order',
                        'order_id': str(order.id)
                    }
                    gcm.plaintext_request(registration_id=clerk.reg_id, data=data)
                except Exception, e:
                    logger.info('exception: ' + str(e))

        # stomp!!!
        stomp_conn.send(body=json.dumps({'message': 'order_paid', 'order': order.get_list_item_info()}), destination='/topic/' + 'payment_channel_' + str(LugatiShoppingSession.objects.filter(cart_id=cart_id)[0].id))


    except Exception, e:
        logger.info('err -> ' + str(e))
    return HttpResponse(json.dumps(res_dt))


def lugati_get_success_payment_template(request):
    cur_site = get_current_site(request)
    cart_items = cart.get_cart_items(request)
    #
    # if cart_items.count() > 0:
    #     order = Order()
    #     #!!!!!
    #     order.cart_id = cart_items[0].cart_id
    #     order.shopping_place = cart_items[0].shopping_place
    #     #~!!!!!
    #     order.site = cur_site
    #     order.save()
    #
    #     for cart_item in cart_items:
    #         order_item = OrderItem()
    #         order_item.order = order
    #         order_item.quantity = cart_item.quantity
    #         order_item.product = cart_item.product
    #         order_item.price = cart_item.product.get_price()
    #         order_item.save()
    #         cart_item.delete()
    logger.info('trying body')

    try:
        #     c_callback = CoinbaseCallback()
        #     c_callback.callback_body = str(request.body)
        #     c_callback.save()
        #     logger.info(str(request.body))
        # except:
        #     logger.info('try failed')

        # data = json.loads(request.body)
        #
        # if ticket <> '':
        #     logger.info('trying create payment transaction')
        #     try:
        sum = 0
        # callback_ticket = CallbackTickets.objects.get(pk=ticket)
        # site = callback_ticket.site
        # cart_items = CartItem.objects.filter(cart_id=callback_ticket.cart_id)
        for cart_item in cart_items:
            sum += cart_item.total()
        logger.info('total sum -> ' + str(sum))
        if cart_items.count() > 0:
            order = Order()
            order.site = cur_site
            #!!!!!
            order.cart_id = cart_items[0].cart_id
            order.shopping_place = cart_items[0].shopping_place
            #~!!!!!
            order.save()

            for cart_item in cart_items:
                order_item = OrderItem()
                order_item.order = order
                order_item.quantity = cart_item.quantity
                order_item.product = cart_item.product
                order_item.price = cart_item.product.get_price()
                order_item.save()
                logger.info('added -> ' + cart_item.product.name + ' ' + str(cart_item.quantity))
                cart_item.delete()
            logger.info('devices' + '1')
            devices = LugatiDevice.objects.filter(shop=order.shopping_place.shop)
            logger.info('devices count' + str(devices.count()))
            reg_ids = []

            for device in devices:
                reg_ids.append(device.reg_id)

            data = {
                'title': "mycelium mps",
                'message': "new order: " + order.shopping_place.name,
                'sound': "beep.wav",
                'url': "http://www.amazon.com",
                'timeStamp': datetime.datetime.now().isoformat(),
                'order_id': order.id,
                'foo': "baz"
            }
            response = gcm.json_request(registration_ids=reg_ids, data=data)
            logger.info('devices: ' + str(response))
            #device.send_message("fuck you")
            #gcm.plaintext_request(registration_id=device.reg_id, data=data)

            #~xmpp
    except Exception, e:
        logger.info('err -> ' + str(e))
    return render(request, 'lugati_shop/mobile/mobile_payment_success.html')


def lugati_get_catalog_template(request):
    return render(request, 'lugati_shop/mobile/mobile_catalog.html')


def lugati_get_cart_base_template(request):
    return render(request, 'lugati_shop/mobile/mobile_cart_base.html')


def lugati_orders_template(request):
    return render(request, 'lugati_shop/mobile/mobile_orders.html')


@csrf_exempt
def lugati_get_catalog_items(request):
    cur_site = get_current_site(request)
    res_dt = {
        'catalog_items': {
            'products': [],
            'categories': []
        },
        'total_categpries_quantity': 0,
        'total_products_quantity': 0
    }

    #parse parameters
    thumbnail_size_str = ''
    if 'thumbnail_size_str' in request.POST:
        thumbnail_size_str = request.POST['thumbnail_size_str']

    cat_id = ''
    if 'cat_id' in request.POST:
        cat_id = request.POST['cat_id']

    cur_brand = ''
    if 'cur_brand' in request.POST:
        cur_brand = request.POST['cur_brand']

    #~parse parameters

    if cat_id <> '':
        products = Product.objects.filter(parent_object=cat_id).filter(is_category=False).filter(site=cur_site)
        categories = Product.objects.filter(parent_object=cat_id).filter(is_category=True).filter(site=cur_site)
    else:
        products = Product.objects.filter(parent_object=None).filter(is_category=False).filter(site=cur_site)
        categories = Product.objects.filter(parent_object=None).filter(is_category=True).filter(site=cur_site)
    #---------------------------------------------------------
    match = resolve(request.POST['cur_url'])
    if match.url_name == 'pos_catalog':
        if settings.LUGATI_SPLIT_CATALOG_BY_SHOP:
            cur_shop = ShoppingPlace.objects.get(pk=match.kwargs['pos_id']).shop
            products = products.filter(shop=cur_shop)
            categories = categories.filter(shop=cur_shop)
    #---------------------------------------------------------

    if cur_brand <> '':
        products = products.filter(brand=Brand.objects.get(pk=cur_brand))

    for product in products:

        try:
            image_tmb = get_thumbnail(product.get_main_image().file, thumbnail_size_str, quality=100)
        except:
            image_tmb = None

        cur_prod = {
            'id': product.id,
            'name': product.name,
            'price': str(product.get_price()).rstrip('0'),
            'preview': product.preview,
            'change_quant': 1,
            'sku': product.sku
        }

        if product.brand:
            cur_prod['brand'] = product.brand.name
            cur_prod['brand_id'] = product.brand.id
        else:
            cur_prod['brand'] = ''
            cur_prod['brand_id'] = ''

        if image_tmb:
            cur_prod['product_url'] = '/catalog/product_details/' + str(product.id)
            cur_prod['main_image_url'] = product.get_main_image().file.url
            #cur_prod['image_url'] = image_tmb.url
            #cur_prod['image_margin'] = margin_str
            cur_prod['image_url'], cur_prod['image_margin'] = product.get_main_image().get_thumbnail_attributes(
                product.get_main_image().get_thumbnail(thumbnail_size_str), thumbnail_size_str)

        else:
            margin_str = '0'

            cur_prod['product_url'] = '/catalog/product_details/' + str(product.id)
            cur_prod['main_image_url'] = ''
            cur_prod['image_url'] = ''
            cur_prod['image_margin'] = margin_str

        res_dt['catalog_items']['products'].append(cur_prod)

        for category in categories:
            cur_cat = {
                'id': category.id,
                'name': category.name,
                'preview': category.preview,
            }

            try:
                image_tmb = get_thumbnail(category.get_main_image().file, thumbnail_size_str, quality=100)
            except:
                image_tmb = None

            if image_tmb:

                #cur_cat['product_url'] = '/catalog/product_details/' + str(product.id)
                cur_cat['main_image_url'] = category.get_main_image().file.url
                cur_cat['image_url'], cur_cat['image_margin'] = category.get_main_image().get_thumbnail_attributes(
                    category.get_main_image().get_thumbnail(thumbnail_size_str), thumbnail_size_str)


            else:
                margin_str = '0'

                #cur_cat['product_url'] = '/catalog/product_details/' + str(product.id)
                cur_cat['main_image_url'] = ''
                cur_cat['image_url'] = ''
                cur_cat['image_margin'] = margin_str

            res_dt['catalog_items']['categories'].append(cur_cat)
    return HttpResponse(json.dumps(res_dt))


#~API

def get_company_title(request, title_id):
    res_dt = {}
    cur_path = request.GET['cur_path']
    resolved_path = resolve(cur_path)
    pos_id = resolved_path.kwargs['pos_id']
    pos = ShoppingPlace.objects.get(pk=pos_id)
    company = pos.shop.company
    if (title_id == 'top'):
        res_dt['title'] = company.top_title
    else:
        res_dt['title'] = company.bottom_title
    return HttpResponse(json.dumps(res_dt))

# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from .models import Order, OrderItem, OrderState
from django.contrib.sites.models import get_current_site
import math
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from lugati.lugati_shop import cart
from lugati.lugati_shop.models import LugatiShoppingSession
from reportlab.pdfgen import canvas
from django.conf import settings
from django.core.urlresolvers import resolve
from django.core.mail import EmailMultiAlternatives
from lugati.lugati_shop import cart
from lugati.lugati_shop.models import ShoppingPlace
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_shop.models import ShoppingPlace, Shop

from django.template.loader import get_template

import logging
from lugati.lugati_shop.models import ShoppingPlace, Shop, LugatiClerk, LugatiCompany, LugatiShoppingSession
from django.template import Context, Template
import cStringIO as StringIO
import ho.pisa as pisa
from cgi import escape
import mimetypes
from django.http import HttpResponse
import os
import urllib
logger = logging.getLogger(__name__)

# def render_to_pdf(template_src, context_dict):
#     template = get_template(template_src)
#     context = Context(context_dict)
#
#     html = template.render(context)
#     result = StringIO.StringIO()
#
#     pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result, encoding='UTF-8')
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), mimetype='application/pdf')
#
#     return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def pdf_receipt(request, object_id=''):
    resp_dt = {}

    order = Order.objects.get(pk=object_id)
    original_filename = 'receipt_' + str(order.id) + '.pdf'
    file_path = order.get_pdf_order_path()

    fp = open(file_path, 'rb')
    response = HttpResponse(fp.read())
    fp.close()
    type, encoding = mimetypes.guess_type(original_filename)
    if type is None:
        type = 'application/octet-stream'
    response['Content-Type'] = type
    response['Content-Length'] = str(os.stat(file_path).st_size)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % original_filename.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        # IE does not support internationalized filename at all.
        # It can only recognize internationalized URL, so we do the trick via routing rules.
        filename_header = ''
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(original_filename.encode('utf-8'))
    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response

@csrf_exempt
def get_orders_list_channel_address(request):
    res_dt = {}
    if request.user.is_authenticated():
        res_dt['channel'] = 'company_orders_' + str(LugatiUserProfile.objects.get(user=request.user).get_company().id)
    else:
        dt = request.GET
        cart_id = cart._cart_id(request)
        if 'cur_path' in dt:
            resolved_path = resolve(dt['cur_path'])
            pos_id = resolved_path.kwargs['pos_id']
            place = ShoppingPlace.objects.get(pk=pos_id)
            cur_company = place.shop.company

        try:
            cur_session = LugatiShoppingSession.objects.get(cart_id=cart_id)
        except:
            cur_session = LugatiShoppingSession()
            cur_session.cart_id = cart_id
            cur_session.company = cur_company
            cur_session.save()
        res_dt['channel'] = 'client_orders_' + str(cur_session.id)

    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def get_channel_address(request):
    dt = request.GET
    cart_id = cart._cart_id(request)
    if request.user.is_authenticated():
        try:
            cur_session = LugatiShoppingSession.objects.get(cart_id=cart_id)
        except:
            cur_session = LugatiShoppingSession()
            cur_session.cart_id = cart_id
            cur_session.is_admin = True
            cur_session.company = LugatiUserProfile.objects.get(user=request.user).get_company()
            cur_session.save()
        return HttpResponse(json.dumps(
            {
                'channel_url': 'ws://' + str(settings.NOTIFICATION_SERVER) + ':' + str(settings.NOTIFICATION_SERVER_PORT) + '/mps_notifications_channel/' + str(dt['channel_type']) + '/' + str(cur_session.id) + '/',
                'session_id': cur_session.id
            }
        ))

    else:
        if 'is_admin' in dt:
            dev_id = dt['dev_id']

            try:
                cur_session = LugatiShoppingSession.objects.get(cart_id=dev_id)
            except:
                cur_session = LugatiShoppingSession()
                cur_session.cart_id = dev_id
                cur_session.is_admin = True
                cur_session.save()

            return HttpResponse(json.dumps({
                'channel_url': 'ws://' + str(settings.NOTIFICATION_SERVER) + ':' + str(settings.NOTIFICATION_SERVER_PORT) +'/mps_notifications_channel/' + str(dt['channel_type']) + '/' + str(cur_session.id) + '/',
                'session_id': cur_session.id}))

        else:
            if 'cur_path' in dt:
                resolved_path = resolve(dt['cur_path'])

                pos_id = resolved_path.kwargs['pos_id']
                place = ShoppingPlace.objects.get(pk=pos_id)
                cur_company = place.shop.company


            logger.info('getting cart_id: ' + str(cart_id))

            try:
                cur_session = LugatiShoppingSession.objects.filter(cart_id=cart_id)[0]
            except:
                cur_session = LugatiShoppingSession()
                cur_session.cart_id = cart_id
                cur_session.company = cur_company
                cur_session.save()

            return HttpResponse(json.dumps({
                'channel_url': 'ws://' + str(settings.NOTIFICATION_SERVER) + ':' + str(settings.NOTIFICATION_SERVER_PORT) +'/mps_notifications_channel/' + str(dt['channel_type']) + '/' + str(cur_session.id) + '/',
                'session_id': cur_session.id}))

def get_pdf_order(request, order_id = ''):
    from io import BytesIO

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_' + order_id + '.pdf"'
    # response['Content-Disposition'] = 'attachment; filename="order_' + order_id + '.pdf"'

    # Create the PDF object, using the response object as its "file."
    buffer = BytesIO()
    # p = canvas.Canvas(response)
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    order = Order.objects.get(pk = order_id)

    top_y = 750
    offset_y = 0
    delta_y = 20
    top_x = 100
    delta_x = 200

    p.drawString(top_x, top_y-offset_y, "num:")
    p.drawString(top_x+delta_x, top_y-offset_y, str(order.id))
    offset_y += delta_y
    p.drawString(top_x, top_y-offset_y, "date:")
    p.drawString(top_x+delta_x, top_y-offset_y, str(order.get_dt()))
    offset_y += delta_y
    p.drawString(top_x, top_y-offset_y, "sum:")
    p.drawString(top_x+delta_x, top_y-offset_y, str(order.get_total_sum()))
    offset_y += delta_y
    p.drawString(top_x, top_y-offset_y, "place:")
    p.drawString(top_x+delta_x, top_y-offset_y, unicode(order.shopping_place.name))

    offset_y += delta_y
    offset_y += delta_y
    offset_y += delta_y

    ind = 1
    for item in order.get_items():
        col_1_w = 20
        col_2_w = 200
        col_3_w = 20
        p.drawString(top_x, top_y-offset_y, str(ind))
        p.drawString(top_x+col_1_w, top_y-offset_y, unicode(item.product.name))
        p.drawString(top_x+col_1_w+col_2_w, top_y-offset_y, str(item.quantity))
        p.drawString(top_x+col_1_w+col_2_w+col_3_w, top_y-offset_y, str(item.get_total_price()))
        offset_y += delta_y
        ind += 1

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    # p.close()
    # response['Content-Length'] = len(response)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def send_order_link_to_email(request, order_id=''):
    email = request.GET['email']
    subject = 'order # ' + order_id + ' pdf'
    message_text = settings.POS_SERVER + 'catalog/lugati_orders/get_pdf_order/' + order_id +'/'
    emails = [email]
    try:
        msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, emails)
        #msg.attach_alternative(message_html, "text/html")
        msg.send()
    except Exception, e:
        i = 1
    return HttpResponse()

@csrf_exempt
def lugati_update_order(request, order_id = ''):
    res_dt = {}
    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def lugati_update_order_state(request, order_id = ''):
    res_dt = {}
    order = Order.objects.get(pk=order_id)
    order.state = OrderState.objects.get(pk=request.POST['new_order_state'])
    order.save()
    res_dt['new_order_state'] = order.state.id
    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def lugati_check_order_state(request, order_id = ''):
    res_dt = {}
    order = Order.objects.get(pk=order_id)
    res_dt['new_order_state'] = order.state.id
    return HttpResponse(json.dumps(res_dt))

#API

def change_order_state(request, order_id, state_id):
    if request.user.is_authenticated():
        order = Order.objects.get(pk=order_id)
        order.state = OrderState.objects.get(pk=state_id)
        order.save()
    return HttpResponse(json.dumps({}))

# @csrf_exempt
# def api_orders(request):
#     if request.method == 'PUT':
#         cur_order = Order.objects.get(pk=request.GET['id'])
#         try:
#             cur_order.state = OrderState.objects.get(pk=request.GET['state'])
#             cur_order.save()
#         except:
#             dt = json.loads(request.body)
#             from lugati.lugati_shop.lugati_orders.forms import NgLugatiOrderEditForm
#
#             form = NgLugatiOrderEditForm(instance=cur_order, data=dt)
#             form.save()
#
#         res_dt = cur_order.get_list_item_info(request)
#         if cur_order.shopping_place :
#             res_dt['place'] = cur_order.shopping_place.name
#         return HttpResponse(json.dumps(res_dt))
#     else: #GET
#         if 'id' in request.GET:
#             if 'cur_path' in request.GET:
#                 resolved_path = resolve(request.GET['cur_path'])
#             cur_order = Order.objects.get(pk=request.GET['id'])
#             if request.user.is_authenticated():
#                 cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
#                 res_dt = cur_order.get_list_item_info(cur_company=cur_company)
#             else:
#                 res_dt = cur_order.get_list_item_info(request)
#
#             #admin features
#             res_dt['admin_features'] = {
#                 'avaliable_options': {
#                     'states': []
#                 },
#                 'cur_values': {
#                     'state': cur_order.state.id
#                 }
#             }
#             for opt in OrderState.objects.all():
#                 res_dt['admin_features']['avaliable_options']['states'].append({
#                     'value': opt.id,
#                     'name': opt.name
#                 })
#
#             return HttpResponse(json.dumps(res_dt))
#         else:
#             res_dt = {
#                 'orders': []
#             }
#
#             if ('is_admin' in request.GET) or request.user.is_authenticated():
#
#                 if (request.GET['is_admin'] == 'true') or (request.user.is_authenticated()):
#                     if settings.SHOP_TYPE == 'MPS':
#                         cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
#                         orders = Order.objects.filter(shopping_place__in=ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=cur_company)))
#                     else:
#                         orders = Order.objects.filter(site=get_current_site(request))
#                 else:
#                     cart_id = cart._cart_id(request)
#                     orders = Order.objects.filter(cart_id=cart_id)
#             else:
#                 cart_id = cart._cart_id(request)
#                 orders = Order.objects.filter(cart_id=cart_id)
#             try:
#                 pos_id = resolve(request.GET['cur_path']).kwargs['pos_id']
#                 cart_id = cart._cart_id(request)
#                 orders = orders.filter(cart_id=cart_id)
#             except:
#                 pass
#             for order in orders:
#                 if ('is_admin' in request.GET) or request.user.is_authenticated():
#                     if (request.GET['is_admin'] == 'true') or request.user.is_authenticated():
#                         ord_item = order.get_list_item_info(cur_company=LugatiUserProfile.objects.get(user=request.user).get_company())
#                     else:
#                         ord_item = order.get_list_item_info(request)
#                 else:
#                     ord_item = order.get_list_item_info(request)
#                 ord_item['items_length'] = 0
#                 ord_item['order_cost'] = 0
#                 order_items = OrderItem.objects.filter(order=order)
#                 for order_item in order_items:
#                     ord_item['items_length'] += order_item.quantity
#
#                 res_dt['orders'].append(ord_item)
#             return HttpResponse(json.dumps(res_dt['orders']))
#~API
@csrf_exempt
def lugati_get_orders(request):

    res_dt = {
        'orders': []
    }
    if 'is_admin' in request.GET:
        orders = Order.objects.all()
    else:
        cart_id = cart._cart_id(request)
        orders = Order.objects.filter(cart_id=cart_id)
    for order in orders:
        ord_item = {
            'order_num': order.id,
            'get_preview': order.get_preview(),
            'items_length': 0,
            'order_cost': 0
        }
        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            ord_item['items_length'] += order_item.quantity

        res_dt['orders'].append(ord_item)
    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def lugati_get_order_details(request, order_id = ''):
    cur_order = Order.objects.get(pk=order_id)
    res_dt = {
        'order_num': order_id,
        'order_date': cur_order.get_dt(),
        'total_sum': cur_order.get_total_sum(),
        'place': cur_order.shopping_place.name,
        'order_items': []
    }

    order_items = OrderItem.objects.filter(order=cur_order)
    for order_item in order_items:
        new_item = {
            'name': order_item.product.name,
            'quantity': order_item.quantity,
            'price': order_item.price,
            'total_price': order_item.get_total_price()
        }

        main_img = order_item.product.get_main_image()
        if main_img:
            new_item['thumbnail_url'], new_item['margin_str'] = main_img.get_thumbnail_attributes(main_img.get_thumbnail('110x110'),'110x110')
        else:
            new_item['thumbnail_url'], new_item['margin_str'] = '', ''

        res_dt['order_items'].append(new_item)
    #admin features
    res_dt['admin_features'] = {
        'avaliable_options': {
            'states': []
        },
        'cur_values': {
            'state': cur_order.state.id
        }
    }
    for opt in OrderState.objects.all():
        res_dt['admin_features']['avaliable_options']['states'].append({
            'value': opt.id,
            'name': opt.name
        })

    return HttpResponse(json.dumps(res_dt))

class CreateOrder(CreateView):
    model = Order

class UpdateOrder(UpdateView):
    model = Order

class DeleteOrder(DeleteView):
    model = Order

class DetailOrder(DetailView):
    model = Order
    template_name = 'lugati_admin/lugati_shop/lugati_orders/order_details.html'

#API
# def lugati_get_order_details_template(request):
#     res_dt = {}
#     if 'is_admin' in request.GET:
#         res_dt['is_admin'] = True
#     return render(request, 'lugati_shop/mobile/mobile_order_details.html', res_dt)
#
# def lugati_get_orders_template(request):
#     return render(request, 'lugati_shop/mobile/mobile_orders.html')


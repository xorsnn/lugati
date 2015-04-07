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
from django.conf import settings
from lugati.lugati_shop.lugati_orders.models import Order
from lugati.lugati_shop.models import ShoppingPlace
from lugati.lugati_registration.models import LugatiUserProfile
from .forms import LugatiOrderEditForm
from django.core.mail import EmailMultiAlternatives
import logging
from django.template import Context
from django.template.loader import get_template
import decimal
logger = logging.getLogger(__name__)


def get_orders_tree(request):
    cur_site = get_current_site(request)
    def get_orders_tree_internal(order_group=None, level=0):
        dt = []
        orders = Order.objects.filter(site=cur_site)
        if settings.LUGATI_SPLIT_CATALOG_BY_SHOP:
            if request.user.is_authenticated():
                orders = orders.filter(shopping_place__in =ShoppingPlace.objects.filter(shop__in=LugatiUserProfile.objects.get(user=request.user).shops.all()))

        for order in orders:
            cur_node = {
                'label': order.get_preview(),
                'uid': order.id,
                'data': {
                    'definition': order.id
                }
            }
            dt.append(cur_node)
        return dt
    res_dt = get_orders_tree_internal()
    return HttpResponse(json.dumps(res_dt))

def get_orders_control_panel(request):
    return render(request, 'lugati_admin/lugati_shop/lugati_orders/orders_control_panel.html')

class UpdateOrder(UpdateView):
    model = Order
    template_name = 'lugati_admin/lugati_shop/lugati_orders/edit_order.html'
    success_url = '/lugati_admin/'

    def get_form_class(self):
        return LugatiOrderEditForm


    def form_invalid(self, form):
        if self.request.is_ajax():
            res_dt = {
                'error': True
            }
            return HttpResponse(json.dumps(res_dt))

    def form_valid(self, form):
        self.object = form.save()

        cur_site = get_current_site(self.request)
        if 'LUGATI_POST_TRACKING' in settings.LUGATI_MODULES:
            order = self.object
            try:
                t = get_template('custom/' + cur_site.name + '/catalog/tracking_template.html')
                message_html = t.render(Context({'order_id': order.id,
                                                 'paid': True,
                                                 'tracking_number' : order.tracking_number,
                                                 'cart_items': OrderItem.objects.filter(order=order),
                                                 'mail': True,
                                                 'email': order.email,
                                                 'phone': order.phone,
                                                 'address': order.address,
                                                 'name': order.name,
                                                 'shop_name': cur_site.name,
                                                 'delivery_price': order.delivery_price,
                                                 'total': decimal.Decimal(order.get_total_sum()) + decimal.Decimal(order.delivery_price)}))

            except:
                t = get_template('lugati_shop/order_mail.html')
                message_html = t.render(Context({'order_id': order.id,
                                                 'paid': True,
                                                 'tracking_number': order.tracking_number,
                                                 'cart_items': OrderItem.objects.filter(order=order),
                                                 'mail': True,
                                                 'email': order.email,
                                                 'phone': order.phone,
                                                 'address': order.address,
                                                 'name': order.name,
                                                 'shop_name': cur_site.name,
                                                 'delivery_price': order.delivery_price,
                                                 'total': decimal.Decimal(order.get_total_sum()) + decimal.Decimal(order.delivery_price)}))

            subject = str(cur_site.domain) + ': Ваш заказ № ' + str(order.id)
            emails  = [order.email]
            try:
                msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
                #msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, emails)
                msg.attach_alternative(message_html, "text/html")
                msg.send()
            except Exception, e:
                logger.error(str(e))

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))
        else:
            return super(UpdateOrder, self).form_valid(form)

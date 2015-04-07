# -*- coding: utf-8 -*-
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.shortcuts import render
from django.http import HttpResponse
from lugati.products.models import Product, Brand

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from lugati.lugati_shop.forms import LugatiClerkForm
from . import cart
from lugati.lugati_shop.lugati_orders.models import Order, OrderItem
from django.template import Context
from .forms import CofirmOrderForm
from django.shortcuts import redirect
from django.template.loader import get_template
import json
from .forms import PhoneForm
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

from lugati.lugati_shop.lugati_delivery.models import DeliveryOption
from lugati.lugati_shop.models import Shop, ShoppingPlace
from lugati.lugati_shop.forms import LugatiShoppingPlaceForm
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_media.models import ThebloqImage
from lugati.lugati_mobile.models import LugatiDevice
logger = logging.getLogger(__name__)

# if settings.HAS_TWILIO:
#     client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)



def get_shopping_places_tree(request):
    def get_shopping_places_tree_internal():
        dt = []
        shopping_places = ShoppingPlace.objects.filter(shop__in=LugatiUserProfile.objects.get(user=request.user).shops.all())
        for shopping_place in shopping_places:
            cur_node = {
                'label': shopping_place.name,
                'uid': shopping_place.id,
                'data': {
                    'definition': shopping_place.name
                }
            }
            dt.append(cur_node)
        return dt
    res_dt = get_shopping_places_tree_internal()
    return HttpResponse(json.dumps(res_dt))

def get_shopping_places_control_panel(request):
    return render(request, 'lugati_admin/lugati_shop/shopping_places_control_panel.html')

#clerks
def get_clerks_tree(request):
    from lugati.lugati_mobile.models import LugatiDevice
    def get_clerks_tree_internal():
        dt = []

        #clerks = Clerk.objects.filter(shop__in=LugatiUserProfile.objects.get(user=request.user).shops.all())
        clerks = LugatiDevice.objects.filter(shop__in=LugatiUserProfile.objects.get(user=request.user).shops.all())
        for clerk in clerks:
            cur_node = {
                'label': clerk.name,
                'uid': clerk.id,
                'data': {
                    'definition': clerk.name
                }
            }
            dt.append(cur_node)
        return dt
    res_dt = get_clerks_tree_internal()
    return HttpResponse(json.dumps(res_dt))

def get_clerks_control_panel(request):
    return render(request, 'lugati_admin/lugati_shop/clerks_control_panel.html')

#phone numbers
def get_phones_tree(request):
    def get_phones_tree_internal():
        dt = []
        objs = PhoneNumber.objects.all()
        for obj in objs:
            cur_node = {
                'label': obj.number,
                'uid': obj.id,
                'data': {
                    'definition': obj.number
                }
            }
            dt.append(cur_node)
        return dt
    res_dt = get_phones_tree_internal()
    return HttpResponse(json.dumps(res_dt))
def get_phones_control_panel(request):
    return render(request, 'lugati_admin/lugati_shop/phones_control_panel.html')
class ListPhoneNumbers(ListView):
    model = PhoneNumber

    template_name = 'lugati_shop/parameters/parameters_list.html'

class CreatePhoneNumber(CreateView):
    model = PhoneNumber
    success_url = '/lugati_admin/phone_notification/'
    template_name = 'lugati_shop/parameters/phonenumber_create_form.html'

    form_class = PhoneForm
    def get_initial(self):
        cur_site = get_current_site(self.request)
        res = {
            'site': cur_site
        }
        return res
    def form_invalid(self, form):
        if self.request.is_ajax():
            res_dt = {
                'error': True
            }
            return HttpResponse(json.dumps(res_dt))
    def form_valid(self, form):
        self.object = form.save()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))
        else:
            return super(UpdatePhoneNumber, self).form_valid(form)
class UpdatePhoneNumber(UpdateView):
    model = PhoneNumber
    success_url = '/lugati_admin/phone_notification/'
    template_name = 'lugati_shop/parameters/phonenumber_form.html'

    form_class = PhoneForm
    def get_initial(self):
        cur_site = get_current_site(self.request)
        res = {
            'site': cur_site
        }
        return res
    def form_invalid(self, form):
        if self.request.is_ajax():
            res_dt = {
                'error': True
            }
            return HttpResponse(json.dumps(res_dt))
    def form_valid(self, form):
        self.object = form.save()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))
        else:
            return super(UpdatePhoneNumber, self).form_valid(form)

class DeletePhoneNumber(DeleteView):
    model = PhoneNumber
    success_url = '/lugati_admin/phone_notification/'
    template_name = 'products/product_confirm_delete.html'


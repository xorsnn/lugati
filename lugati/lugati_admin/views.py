# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.conf import settings
from lugati.lugati_points_of_sale.models import SalesPoint
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from lugati.lugati_shop.models import PhoneNumber
from django.contrib.sites.models import get_current_site
from .forms import BrandForm
from lugati.products.models import Brand, Product
import locale
import sys

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
import json
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_media.forms import NgThebloqVideoForm
from django.views.decorators.csrf import csrf_exempt
from lugati.lugati_shop.lugati_orders.models import Order
from lugati.lugati_admin.forms import LugatiRegistrationForm, LugatiAuthForm, LugatiPasswordRestoreRequestForm, LugatiPasswordRestoreForm
import datetime
from django.views.generic.edit import FormView
from registration.models import RegistrationProfile
from django.contrib.sites.models import RequestSite
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationForm
from django.utils.encoding import force_text
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from registration import signals
from lugati.lugati_admin.models import PasswordRestoreRequest
import random
from django.contrib.auth.models import User
#super new
import logging
from django.http import Http404
from django.core.urlresolvers import resolve
logger = logging.getLogger(__name__)

def check_if_logged_in(request):
    resp_data = {}

    if request.user.is_authenticated():
        resp_data['is_logged_in'] = True
    else:
        resp_data['is_logged_in'] = False
    resp_data['redirect_url'] = settings.POS_SERVER + '/lugati_admin/'
    return HttpResponse(json.dumps(resp_data))


@csrf_exempt
def device_login(request):
    resp_data = {}
    logger.info('trying device login')

    # username = request.GET['username']
    # password = request.GET['password']
    # reg_id = request.GET['reg_id']
    body_dt = json.loads(request.body)
    username = body_dt['params']['username']
    password = body_dt['params']['password']
    reg_id = body_dt['params']['reg_id']
    logger.info('reg_id: ' + reg_id)
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            from lugati.lugati_shop.models import LugatiClerk
            # try:
            clerk = LugatiClerk.objects.get(user=user)
            clerk.reg_id = reg_id
            clerk.save()
            # except Exception, e:
            #     pass

            resp_data['result'] = 'success'
            resp_data['redirect_url'] = settings.POS_SERVER + '/lugati_admin/'
        else:
            resp_data['result'] = 'error'
    else:
        resp_data['result'] = 'error'

    return HttpResponse(json.dumps(resp_data))

def password_restore(request):
    response_data = {}
    if request.method == 'POST':
        form = LugatiPasswordRestoreForm(data=json.loads(request.body))

        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data
                new_password = cleaned_data['new_password1']
                user = PasswordRestoreRequest.objects.get(code=cleaned_data['request_code']).user
                user.set_password(new_password)
                user.save()
            except Exception, e:
                response_data['errors'] = {'new_password2': 'no request code'}
        else:
            response_data['errors'] = form.errors
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data['restore_allowed'] = False
        if 'request_code' in request.GET:
            try:
                req = PasswordRestoreRequest.objects.get(code=request.GET['request_code'])
                response_data['restore_allowed'] = True
                response_data['password_restore_form'] = LugatiPasswordRestoreForm()
                response_data['password_restore_form'].fields['request_code'].initial = request.GET['request_code']
            except:
                pass
        return render(request, 'registration/password_restore.html', response_data)

def password_restore_request(request):
    response_data = {}
    if request.method == 'POST':
        form = LugatiPasswordRestoreRequestForm(data=json.loads(request.body))
        if form.is_valid():
            cleaned_data = form.cleaned_data
            email = cleaned_data['email']

            from datetime import timedelta
            request_code = ''
            characters = 'abcdefghijklmnopqrstuvwxyz1234567890'
            request_code_length = 100
            for y in range(request_code_length):
                request_code += characters[random.randint(0, len(characters)-1)]

            # now = datetime.datetime.now()
            # delta = timedelta(days=1)
            # todo!!!
            usr = User.objects.get(email=email)
            req = PasswordRestoreRequest()
            req.code = request_code
            req.user = usr
            req.save()

            ctx_dict = {'request_code': request_code,
                        'cur_domain': settings.POS_SERVER,
                        'user': usr}

            subject = 'mycelium order password restore'
            message = render_to_string('registration/password_restore_email.html',
                                       ctx_dict)

            emails = [email]
            message_html = message
            try:
                msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
                msg.attach_alternative(message_html, "text/html")
                msg.send()
            except Exception, e:
                logger.error(str(e))

            # return new_user
        else:
            response_data['errors'] = form.errors
            # response_data['success_url'] = force_text(success_url)
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def lugati_register(request):
    response_data = {}
    if request.method == 'POST':
        form = LugatiRegistrationForm(data=json.loads(request.body))
        if form.is_valid():
            cleaned_data = form.cleaned_data

            username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']

            if Site._meta.installed:
                site = Site.objects.get_current()
            else:
                site = RequestSite(request)

            new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                        password, site, False)

            #mail
            reg_prof = RegistrationProfile.objects.get(user=new_user)
            ctx_dict = {'activation_key': reg_prof.activation_key,
                        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                        'site': site,
                        'cur_domain': settings.POS_SERVER,
                        'user': new_user}
            subject = render_to_string('registration/activation_email_subject.txt',
                                       ctx_dict)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())

            message = render_to_string('registration/activation_email.html',
                                       ctx_dict)

            # new_user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

            emails = [new_user.email]
            message_html = message
            try:
                msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
                msg.attach_alternative(message_html, "text/html")
                msg.send()
            except Exception, e:
                logger.error(str(e))
            #~mail

            signals.user_registered.send(sender="lugati_register",
                                         user=new_user,
                                         request=request)
            # return new_user
        else:
            response_data['errors'] = form.errors
            # response_data['success_url'] = force_text(success_url)
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def lugati_login(request):
    success_url = '/lugati_admin/#/mps_catalog/'
    if request.method == 'POST':
        form = AuthenticationForm(data=json.loads(request.body))
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # resp_data['result'] = 'success'
                else:
                    # resp_data['result'] = 'error'
                    pass
            else:
                pass
                # resp_data['result'] = 'error'
        response_data = {'errors': form.errors, 'success_url': force_text(success_url)}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect('/lugati_admin/')
        else:
            params = {
                'auth_form': LugatiAuthForm,
                'register_form': LugatiRegistrationForm,
                'password_restore_request_form': LugatiPasswordRestoreRequestForm
            }

            return render(request, 'lugati_admin/lugati_version_1_0/login.html', params)

def lugati_ajax_logout(request):
    logout(request)
    return HttpResponse(json.dumps({}))

def lugati_logout(request):
    logout(request)
    return HttpResponseRedirect('/lugati_admin/')

#new admin
def get_editing_template(request):
    resp_data = {}
    return render(request, 'lugati_admin/editing_template.html', resp_data)

# class LugatiEditObject(FormView):

def get_objects_list_form(request, content_object_id='', cat_id=''):
    resp_dt = {}
    cur_site = get_current_site(request)
    if content_object_id <> '':

        model_class = ContentType.objects.get(pk=content_object_id).model_class()

        if model_class.__name__ == 'Order':
            return render(request, 'lugati_admin/lugati_version_1_0/orders/ng_orders_template.html')
        # elif model_class.__name__ == 'ShoppingPlace':
        #     return render(request, 'lugati_admin/lugati_version_1_0/order_points/order_points_list_mps.html')
        elif model_class.__name__ == 'Product':
            if 'obj_type' in request.GET:
                if request.GET['obj_type'] == 'topping':
                    return render(request, 'lugati_admin/lugati_version_1_0/plugins/toppings/objects_list_mps.html', resp_dt)

    return render(request, 'lugati_admin/lugati_version_1_0/objects_list_mps.html', resp_dt)

def get_edit_object_form(request, content_object_id, object_id):

    resp_dt = {}
    cur_site = get_current_site(request)
    model_class = ContentType.objects.get(pk=content_object_id).model_class()
    try:
        obj = model_class.objects.get(pk=object_id)
    except:
        raise Http404("Can't edit")

    can_edit = False
    if request.user.is_authenticated():
        if settings.SHOP_TYPE == "MPS":
            if hasattr(model_class, 'company'):
                if obj.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                    can_edit = True
            else:
                if model_class.__name__ ==  'LugatiCompany':
                    if obj == LugatiUserProfile.objects.get(user=request.user).get_company():
                        can_edit = True

                elif model_class.__name__ ==  'ShoppingPlace':
                    if obj.shop.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                        can_edit = True
                elif model_class.__name__ == 'Order':
                    if obj.shopping_place.shop.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                        can_edit = True
                else:
                    pass
        else:
            can_edit = True
    else:
        if settings.SHOP_TYPE == "MPS":
            if 'cur_path' in request.GET:
                resolved_path = resolve(request.GET['cur_path'])
                try:
                    pos_id = resolved_path.kwargs['pos_id']
                    place = ShoppingPlace.objects.get(pk=pos_id)
                    cur_company = place.shop.company
                    if hasattr(model_class, 'company'):
                        if obj.company == cur_company:
                            can_edit = True
                        else:
                            if model_class.__name__ == 'ShoppingPlace':
                                if obj.shop.company == cur_company:
                                    can_edit = True
                            else:
                                pass
                except:
                    pass
            elif model_class.__name__ == 'Order':
                can_edit = True
        else:
            can_edit = True
    if can_edit:
        resp_dt['object'] = obj
    else:
        raise Http404("Can't edit")

    if model_class.__name__ == 'LugatiClerk':

        from lugati.lugati_shop.forms import NgLugatiClerkForm
        try:
            resp_dt['waiter_login'] = obj.user.username
        except:
            pass
        resp_dt['form'] = NgLugatiClerkForm(request=request, instance=resp_dt['object'])

    if model_class.__name__ == 'Order':
        from lugati.lugati_shop.lugati_orders.models import OrderState, Order

        resp_data = {
            'lugati_debug': settings.DEBUG,
            'cur_site_name': cur_site.name,
            'request': request
        }
        if settings.SHOP_TYPE == 'MPS':
            resp_data['order'] = obj.get_list_item_info(request)
            if request.user.is_authenticated():
                order = obj
                if order.state.name == 'PAID':
                    order.state = OrderState.objects.get(name="ACKNOWLEDGED")
                    order.save()
            from lugati.lugati_shop.models import LugatiClerk
            return render(request, 'lugati_admin/lugati_version_1_0/orders/ng_order_details_template.html', resp_data)
        else:
            from lugati.lugati_shop.lugati_orders.forms import NgLugatiOrderEditForm
            resp_data['form'] = NgLugatiOrderEditForm(instance=obj)
            resp_data['object'] = obj
            return render(request, 'lugati_admin/lugati_version_1_0/shop/sola/edit_order_form.html', resp_data)

    elif model_class.__name__ == 'LugatiTextBlock':
        from lugati.lugati_widgets.forms import NgLugatiTextBlockForm
        resp_dt['form'] = NgLugatiTextBlockForm(instance=resp_dt['object'])

    elif model_class.__name__ == 'Product':
        from lugati.products.forms import NgProductForm, NgCategoryForm, NgToppingForm
        if obj.is_topping:
            resp_dt['form'] = NgToppingForm(request=request, instance=resp_dt['object'])
            return render(request, 'lugati_admin/lugati_version_1_0/plugins/toppings/edit_object_form_mps.html', resp_dt)
        else:
            if resp_dt['object'].is_category:
                resp_dt['form'] = NgCategoryForm(request=request, instance=resp_dt['object'])
            else:
                resp_dt['form'] = NgProductForm(request=request, instance=resp_dt['object'])
        # return render(request, 'lugati_admin/lugati_version_1_0/products/edit_object_form_mps.html', resp_dt)
        return render(request, 'lugati_admin/lugati_version_1_0/edit_object_form_mps.html', resp_dt)

    elif model_class.__name__ == 'City':
        from lugati.lugati_points_of_sale.forms import NgCityForm
        resp_dt['form'] = NgCityForm(site=cur_site, instance=resp_dt['object'])

    elif model_class.__name__ == 'LugatiPortfolioItem':
        from lugati.lugati_widgets.forms import NgLugatiPortfolioItemForm
        resp_dt['form'] = NgLugatiPortfolioItemForm(instance=resp_dt['object'])

    elif model_class.__name__ == 'DeliveryOption':
        from lugati.lugati_shop.lugati_delivery.forms import NgDeliveryOptionForm
        resp_dt['form'] = NgDeliveryOptionForm(request=request, instance=resp_dt['object'])

    elif model_class.__name__ == 'DeliveryPrice':
        from lugati.lugati_shop.lugati_delivery.forms import NgDeliveryPriceForm
        resp_dt['form'] = NgDeliveryPriceForm(request=request, instance=resp_dt['object'])

    elif model_class.__name__ == 'SalesPoint':
        from lugati.lugati_points_of_sale.forms import NgPosForm
        resp_dt['form'] = NgPosForm(site=cur_site,instance=resp_dt['object'])

    elif model_class.__name__ == 'ThebloqVideo':
        resp_dt['form'] = NgThebloqVideoForm(instance=resp_dt['object'])

    elif model_class.__name__ == 'Shop':
        from lugati.lugati_shop.forms import NgShopForm
        resp_dt['form'] = NgShopForm(request=request,instance=resp_dt['object'])
        resp_dt['lugati_editing'] = True

    elif model_class.__name__ == 'ShoppingPlace':
        from lugati.lugati_shop.forms import NgEditShoppingPlaceForm
        resp_dt['form'] = NgEditShoppingPlaceForm(request=request,instance=resp_dt['object'])
        resp_dt['lugati_editing'] = True
        return render(request, 'lugati_admin/lugati_version_1_0/order_points/edit_order_point_mps.html', resp_dt)

    elif model_class.__name__ == 'GalleryItem':
        from lugati.lugati_media.lugati_gallery.forms import NgGalleryItemForm
        resp_dt['form'] = NgGalleryItemForm(request=request, instance=resp_dt['object'])
        resp_dt['lugati_editing'] = True

    elif model_class.__name__ == 'LugatiPoem':
        from lugati.lugati_widgets.forms import NgLugatiPoemForm
        resp_dt['form'] = NgLugatiPoemForm(instance=resp_dt['object'])
        resp_dt['lugati_editing'] = True

    elif model_class.__name__ == 'LugatiNews':
        from lugati.lugati_widgets.forms import NgLugatiNewsForm
        resp_dt['form'] = NgLugatiNewsForm(instance=resp_dt['object'])
        resp_dt['lugati_editing'] = True

    elif model_class.__name__ == 'LugatiCompany':
        from lugati.lugati_shop.forms import NgLugatiCompanyForm
        resp_dt['form'] = NgLugatiCompanyForm(instance=resp_dt['object'])
        resp_dt['lugati_editing'] = True
        resp_dt['STRIPE_CLIENT_ID'] = settings.STRIPE_CLIENT_ID
        return render(request, 'lugati_admin/lugati_version_1_0/company/edit_object_form_mps.html', resp_dt)

    elif model_class.__name__ == 'LugatiDevice':
        from lugati.lugati_mobile.forms import NgLugatiDeviceForm
        from lugati.lugati_shop.models import ShoppingPlace
        from django import forms
        resp_dt['form'] = NgLugatiDeviceForm(instance=resp_dt['object'])
        resp_dt['form'].fields['shopping_place'] = forms.ModelChoiceField(queryset=ShoppingPlace.objects.filter(shop__in=LugatiUserProfile.objects.get(user=request.user).shops.all()),
                                                             widget=forms.Select(attrs={'class':'form-control'}),
                                                             required=False,
                                                             label=_(u'Shopping place'))

    return render(request, 'lugati_admin/lugati_version_1_0/edit_object_form_mps.html', resp_dt)

def get_create_object_form(request, content_object_id):
    resp_dt = {}
    cur_site = get_current_site(request)
    model_class = ContentType.objects.get(pk=content_object_id).model_class()

    if model_class.__name__ == 'LugatiClerk':
        from lugati.lugati_shop.forms import NgLugatiClerkForm
        resp_dt['form'] = NgLugatiClerkForm(request=request)

    if model_class.__name__ == 'LugatiTextBlock':
        from lugati.lugati_widgets.forms import NgLugatiTextBlockForm
        resp_dt['form'] = NgLugatiTextBlockForm

    elif model_class.__name__ == 'SalesPoint':
        from lugati.lugati_points_of_sale.forms import NgPosForm
        resp_dt['form'] = NgPosForm(site=cur_site, initial={'site': cur_site})

    elif model_class.__name__ == 'LugatiPoem':
        from lugati.lugati_widgets.forms import NgLugatiPoemForm
        resp_dt['form'] = NgLugatiPoemForm(initial={'site': cur_site})

    elif model_class.__name__ == 'LugatiPortfolioItem':
        from lugati.lugati_widgets.forms import NgLugatiPortfolioItemForm
        resp_dt['form'] = NgLugatiPortfolioItemForm(initial={'site': cur_site})

    elif model_class.__name__ == 'City':
        from lugati.lugati_points_of_sale.forms import NgCityForm
        resp_dt['form'] = NgCityForm(site=cur_site, initial={'site': cur_site})

    elif model_class.__name__ == 'DeliveryOption':
        from lugati.lugati_shop.lugati_delivery.forms import NgDeliveryOptionForm
        resp_dt['form'] = NgDeliveryOptionForm(request=request, initial={'site': cur_site})

    elif model_class.__name__ == 'DeliveryPrice':
        from lugati.lugati_shop.lugati_delivery.forms import NgDeliveryPriceForm
        resp_dt['form'] = NgDeliveryPriceForm(request=request)

    elif model_class.__name__ == 'LugatiNews':
        from lugati.lugati_widgets.forms import NgLugatiNewsForm
        resp_dt['form'] = NgLugatiNewsForm(initial={'site': cur_site})

    elif model_class.__name__ == 'Product':
        from lugati.products.forms import NgProductForm, NgCategoryForm, NgToppingForm

        if 'is_category' in request.GET:
            resp_dt['form'] = NgCategoryForm(request=request, initial={'site': cur_site, 'is_category': True, 'company': LugatiUserProfile.objects.get(user=request.user).get_company()})
        else:
            resp_dt['form'] = None
            if 'obj_type' in request.GET:
                if request.GET['obj_type'] == 'topping':
                    resp_dt['form'] = NgToppingForm(request=request)
                    return render(request, 'lugati_admin/lugati_version_1_0/plugins/toppings/create_object_form_mps.html', resp_dt)
            if not resp_dt['form']:
                resp_dt['form'] = NgProductForm(request=request, initial={'site': cur_site, 'company':LugatiUserProfile.objects.get(user=request.user).get_company()})
                return render(request, 'lugati_admin/lugati_version_1_0/create_object_form.html', resp_dt)

    elif model_class.__name__ == 'ThebloqVideo':
        resp_dt['form'] = NgThebloqVideoForm(initial={'site': cur_site})

    elif model_class.__name__ == 'ShoppingPlace':
        from lugati.lugati_shop.forms import NgShoppingPlaceForm

        resp_dt['form'] = NgShoppingPlaceForm(request=request)

    elif model_class.__name__ == 'Shop':
        from lugati.lugati_shop.forms import NgShopForm
        resp_dt['form'] = NgShopForm(request=request)
    elif model_class.__name__ == 'GalleryItem':
        from lugati.lugati_media.lugati_gallery.forms import NgGalleryItemForm
        resp_dt['form'] = NgGalleryItemForm(request=request)

    return render(request, 'lugati_admin/lugati_version_1_0/create_object_form.html', resp_dt)

def lugati_editing_template(request):
    resp_data = {}
    cur_site = get_current_site(request)
    # if cur_site.name == 'mps':
    return render(request, 'lugati_admin/editing_template_mps.html', resp_data)
    # else:
    #     return render(request, 'lugati_admin/editing_template.html', resp_data)

def new_lugati_admin(request):
    cur_site = get_current_site(request)
    resp_data = {}
    if request.user.is_authenticated():
        resp_data['request'] = request
        resp_data['user'] = request.user
        resp_data['debug'] = settings.DEBUG
        resp_data['cur_site_name'] = cur_site.name
        resp_data['admin_page'] = True

        if settings.SHOP_TYPE == 'MPS':
            resp_data['redirect_hash'] = '/mps_catalog/'
        else:
            resp_data['redirect_hash'] = '/'

        prof = LugatiUserProfile.objects.get(user=request.user)
        from lugati.lugati_registration.models import LugatiRole
        role = LugatiRole.objects.get(name='waiter')

        if role in prof.roles.all():
            resp_data['is_device'] = True
            resp_data['redirect_hash'] = '/view/' + str(ContentType.objects.get_for_model(Order).id)
        else:
            resp_data['is_device'] = False

        return render(request, 'lugati_admin/lugati_version_1_0/main.html', resp_data)
    else:
        return HttpResponseRedirect('/lugati_admin/lugati_login/')

def get_tree_template(request):
    return render(request, 'lugati_admin/tree_template.html')

def main(request):
    resp_data = {}
    return render(request, 'lugati_admin/lugati_version_1_0/lugati_main.html', resp_data)

def first_start(request):
    resp_data = {}
    return render(request, 'lugati_admin/lugati_version_1_0/start_wisard.html', resp_data)

def user_settings(request):
    resp_data = {}
    return render(request, 'lugati_admin/lugati_version_1_0/lugati_user_settings.html', resp_data)

def company_settings(request):
    resp_data = {}
    from lugati.lugati_shop.forms import NgLugatiCompanyForm
    prof = LugatiUserProfile.objects.get(user=request.user)
    resp_data['object'] = prof.get_company()
    resp_data['form'] = NgLugatiCompanyForm(instance=resp_data['object'])
    resp_data['lugati_editing'] = True

    return render(request, 'lugati_admin/lugati_version_1_0/edit_object_form_mps.html', resp_data)
    # return render(request, 'lugati_admin/lugati_version_1_0/lugati_company_settings.html', resp_data)

def shops(request):
    resp_data = {}
    return render(request, 'lugati_admin/lugati_shop/shop.html', resp_data)

#~new admin

def check_licensing(request):

    res_dt = {
        'license_accepted': False
    }

    try:
        prof = LugatiUserProfile.objects.get(user=request.user)
        res_dt['license_accepted'] = prof.license_accepted
    except:
        res_dt['license_accepted'] = False

    return HttpResponse(json.dumps(res_dt))

def accept_license(request):

    res_dt = {
        'license_accepted': False
    }

    try:
        prof = LugatiUserProfile.objects.get(user=request.user)
        if request.GET['license_accepted'] == 'true':
            prof.license_accepted = True
            prof.save()
            res_dt['license_accepted'] = True
        else:
            prof.license_accepted = False
            prof.save()
            res_dt['license_accepted'] = False

        return HttpResponse(json.dumps(res_dt))

    except:
        return HttpResponse(json.dumps(res_dt))
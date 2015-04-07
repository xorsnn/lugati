# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.sites.models import get_current_site
from lugati.products.models import Product, ProductProperty, ProductPropertyValue, ProductPrice
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
import json
import logging
from django.views.decorators.csrf import csrf_exempt
import lugati.lugati_procs as lugati_procs
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_shop.models import ShoppingPlace, Shop
from lugati.lugati_mobile.models import LugatiDevice
from django import forms
from django.contrib.flatpages.models import FlatPage
from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from lugati.lugati_media.models import ThebloqImage
from lugati.lugati_shop.models import LugatiCompany
from lugati.lugati_widgets.models import LugatiPortfolioItem
from django.core.urlresolvers import resolve
from lugati.lugati_shop.lugati_orders.models import OrderItem, Order, OrderState
from lugati.lugati_shop import cart
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django.template import Context
from django.template.loader import get_template
import datetime
from lugati.lugati_shop.models import LugatiClerk

from HTMLParser import HTMLParser
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Max
# strip html
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
# ~strip html

logger = logging.getLogger(__name__)

@csrf_exempt
def request_test(request):
    res_dt = {
        'method': request.method,
        'body': request.body
    }
    return HttpResponse(json.dumps(res_dt))


@csrf_exempt
def api_objects(request, content_object_id, object_id=''):
    cur_site = get_current_site(request)
    model_class = ContentType.objects.get(pk=content_object_id).model_class()

    if request.method == 'GET':
        if object_id <> '':
            obj = model_class.objects.get(pk=object_id)
            #======================

            can_edit = False
            if request.user.is_authenticated():
                if settings.SHOP_TYPE == "MPS":
                    if hasattr(model_class, 'company'):
                        if obj.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                            can_edit = True
                    else:
                        if model_class.__name__ == 'LugatiCompany':
                            if obj == LugatiUserProfile.objects.get(user=request.user).get_company():
                                can_edit = True

                        elif model_class.__name__ == 'ShoppingPlace':
                            if obj.shop.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                                can_edit = True
                        elif model_class.__name__ == 'Order':
                            if obj.shopping_place.shop.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                                can_edit = True
                        elif model_class.__name__ == 'Tooltip':
                            can_edit = True
                        elif model_class.__name__ == 'ThebloqImage':
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
                                elif model_class.__name__ == 'Order':
                                    if obj.shopping_place.shop.company == cur_company:
                                        can_edit = True
                                else:
                                    pass
                        except:
                            pass
                else:
                    can_edit = True

            # if can_edit:
            #     resp_dt['object'] = obj
            # else:
            #     raise Http404("Can't edit")

            #======================
            if can_edit:
                try:
                    if model_class.__name__ == 'Product':
                        node = obj.get_list_item_info(request, hierarchy=True)
                    elif model_class.__name__ == 'Tooltip':
                        node = obj.get_list_item_info(request)
                    elif model_class.__name__ == 'Order':
                        if not obj.clerk:
                            if request.user.is_authenticated():
                                if 'is_device' in request.GET:
                                    if request.GET['is_device']:
                                        clerk = LugatiClerk.objects.get(user=request.user)
                                        obj.clerk = clerk
                                        if obj.state.name == 'PAID':
                                            obj.state = OrderState.objects.get(name="ACKNOWLEDGED")
                                        obj.save()
                        node = obj.get_list_item_info(request)
                    else:
                        node = obj.get_list_item_info(request)
                except Exception, e:
                    logger.info(str(e))
                    node = {
                        'id': obj.id,
                        'name': str(obj)
                    }
            else:
                node = {}
            return HttpResponse(json.dumps(node))
        else:

            #======================
            cur_company = None

            if settings.SHOP_TYPE == "MPS":

                if 'cur_path' in request.GET:
                    resolved_path = resolve(request.GET['cur_path'])
                    try:
                        pos_id = resolved_path.kwargs['pos_id']
                        place = ShoppingPlace.objects.get(pk=pos_id)
                        cur_company = place.shop.company
                    except:
                        pass
                if (cur_company == None) and request.user.is_authenticated():
                    cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
            #======================

            res_dt = []
            if (cur_company and settings.SHOP_TYPE=='MPS') or (settings.SHOP_TYPE <> 'MPS'):
                if model_class.__name__ == 'Shop':
                    objects = Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company())
                if model_class.__name__ == 'LugatiClerk':
                    objects = LugatiClerk.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company())
                elif model_class.__name__ == 'ShoppingPlace':
                    objects = ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company()))
                elif model_class.__name__ == 'LugatiDevice':
                    objects = LugatiDevice.objects.filter(shop__in=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company()))
                elif model_class.__name__ == 'LugatiCompany':
                    objects = LugatiCompany.objects.filter(pk=LugatiUserProfile.objects.get(user=request.user).get_company().id)
                elif model_class.__name__ == 'Product':
                    objects = Product.objects.filter(site=cur_site)
                    if settings.SHOP_TYPE == 'MPS':
                        if request.user.is_authenticated():
                            cur_profile = LugatiUserProfile.objects.get(user=request.user)
                            objects = objects.filter(company=cur_profile.get_company())
                        else:
                            try:
                                match = resolve(request.GET['cur_path'])
                                pos_id = match.kwargs['pos_id']
                                cur_company = ShoppingPlace.objects.get(pk=pos_id).shop.company
                                objects = objects.filter(company=cur_company)
                            except Exception, e:
                                objects = objects.filter(company=None)
                                pass

                    parent_object = None
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
                            objects = objects.filter(is_category=False).filter(is_topping=True)
                            if not request.user.is_authenticated():
                                objects = objects.filter(assigned_to__in=[request.GET['assigned_to_id']])
                            if 'assigning' in request.GET:
                                if request.GET['assigning']:
                                    objects = objects.filter(parent_object=Product.objects.get(pk=request.GET['parent_id']))
                            # else:
                            #
                        else:
                            objects = objects.filter(is_topping=False)
                    else:
                        objects = objects.filter(is_topping=False)
                        objects = objects.filter(parent_object=parent_object)

                    #todo brands
                    # if (brand_id <> ''):
                    #     objects = objects.filter(brand=Brand.objects.get(pk=brand_id))
                    # elif ('brand_id' in request.GET):
                    #     objects = objects.filter(brand=Brand.objects.get(pk=request.GET['brand_id']))

                    #~filter

                elif model_class.__name__ == 'Order':
                    if ('is_admin' in request.GET) or request.user.is_authenticated():
                        if (request.GET['is_admin'] == 'true') or (request.user.is_authenticated()):
                            if settings.SHOP_TYPE == 'MPS':
                                cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
                                objects = Order.objects.filter(shopping_place__in=ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=cur_company)))
                            else:
                                objects = Order.objects.filter(site=get_current_site(request))
                            if ('period' in request.GET):
                                period = json.loads(request.GET['period'])
                                date_from = datetime.datetime.strptime(period['date_from'], "%Y-%m-%d")
                                date_to = datetime.datetime.strptime(period['date_to'], "%Y-%m-%d")
                                delta = datetime.timedelta(days=1)
                                microsecond = datetime.timedelta(microseconds=1)
                                delta = delta - microsecond
                                objects = objects.filter(dt_add__range=[date_from, date_to+delta])
                            if ('is_device' in request.GET):
                                if (request.GET['is_device']):
                                    avaliable_states = OrderState.objects.filter(name__in=['PAID','ACKNOWLEDGED'])
                                    avalible_clerk = LugatiClerk.objects.get(user=request.user)
                                    objects = objects.filter(state__in=avaliable_states).filter(Q(clerk=avalible_clerk) | Q(clerk=None))

                        else:
                            cart_id = cart._cart_id(request)
                            objects = Order.objects.filter(cart_id=cart_id)
                    else:
                        cart_id = cart._cart_id(request)
                        objects = Order.objects.filter(cart_id=cart_id)
                    try:
                        if 'pos_id' in resolve(request.GET['cur_path']).kwargs:
                            pos_id = resolve(request.GET['cur_path']).kwargs['pos_id']
                            cart_id = cart._cart_id(request)
                            objects = objects.filter(cart_id=cart_id)
                    except:
                        pass

                    for order in objects:
                        ord_item = order.get_list_item_info(request)
                        ord_item['items_length'] = 0
                        ord_item['order_cost'] = 0
                        order_items = OrderItem.objects.filter(order=order)
                        for order_item in order_items:
                            ord_item['items_length'] += order_item.quantity

                else:
                    if lugati_procs.is_hierarchical(ContentType.objects.get(pk=content_object_id)):
                        parent_object = None
                        if 'parent_object' in request.GET:
                            parent_object = request.GET['parent_object']
                        objects = model_class.objects.filter(parent_object=parent_object)
                    else:
                        objects = model_class.objects.all()

                if hasattr(model_class, 'site'):
                    objects = objects.filter(site=cur_site)

                for object in objects:
                    if model_class.__name__ == 'Product' and settings.SHOP_TYPE=='MPS':
                        if object.styled_name.strip() == '':
                            object.delete()
                            continue
                    try:
                        node = object.get_list_item_info(request)
                    except:
                        node = {
                            'id': object.id,
                            'name': str(object)
                        }
                    res_dt.append(node)

            return HttpResponse(json.dumps(res_dt))

    elif request.method == 'POST':
        res_dt = {}

        object_dt = json.loads(request.body)

        can_edit = False
        if request.user.is_authenticated():
            if settings.SHOP_TYPE == "MPS":
                if hasattr(model_class, 'company'):
                    object_dt['company'] = LugatiUserProfile.objects.get(user=request.user).get_company().id
                elif hasattr(model_class, 'shop'):
                    object_dt['shop'] = Shop.objects.get(company=LugatiUserProfile.objects.get(user=request.user).get_company()).id
                can_edit = True
            else:
                #todo handle different sites
                can_edit = True
                # can_edit = False

        if not can_edit:
            #todo handle can't edit case
            pass
        elif model_class.__name__ == 'ProductPropertyValue':
            if settings.SHOP_TYPE == 'MPS':
                object_dt = json.loads(request.body)
                try:
                    product = Product.objects.get(pk=object_dt['product_id'])
                    priceable = object_dt['priceable']
                    if priceable:
                        if ProductProperty.objects.filter(product=product, name='mps_priceable').exists():
                            prop = ProductProperty.objects.get(product=product, name='mps_priceable')
                        else:
                            prop = ProductProperty()
                            prop.product = product
                            prop.name = 'mps_priceable'
                            prop.save()
                    else:
                        if ProductProperty.objects.filter(product=product, name='mps_not_priceable').exists():
                            prop = ProductProperty.objects.get(product=product, name='mps_not_priceable')
                        else:
                            prop = ProductProperty()
                            prop.product = product
                            prop.name = 'mps_not_priceable'
                            prop.save()

                    prop_value = ProductPropertyValue()
                    prop_value.product_property = prop

                    if ('value' in object_dt):
                        prop_value.value = object_dt['value']
                    else:
                        prop_value.value = 'new'

                    if ('name' in object_dt):
                        prop_value.name = object_dt['name']
                    else:
                        prop_value.name = ''

                    if ('default' in object_dt):
                        prop_value.default = object_dt['default']

                    prop_value.save()
                    if 'price' in object_dt:
                        #doing
                        try:
                            prod_price = ProductPrice.objects.get(product=prop.product, product_property_value=prop_value)
                        except:
                            prod_price = ProductPrice()
                            prod_price.product = prop.product
                            prod_price.product_property_value = prop_value
                        prod_price.price = object_dt['price']
                        prod_price.save()

                    res_dt = prop_value.get_list_item_info(request)

                except Exception, e:
                    logger.info(str(e))

        elif model_class.__name__ == 'LugatiClerk':
            user = None
            error = False
            try:
                index = int(User.objects.all().aggregate(Max('id'))['id__max'])
            except:
                res_dt['error'] = True
                res_dt['error_msg'] = 'Error while getting latest user index.'
                error = True
            if not error:
                iterations = 10
                user_created = False
                while ((not user_created) and (iterations > 0)):
                    index += 1
                    new_username = settings.WAITER_NAME_PREFIX + '_' + str(index)
                    if not User.objects.filter(username=new_username).exists():
                        user = User.objects.create_user(username=new_username,
                                                    email=new_username + '@mycelium.com',
                                                    password=object_dt['password'])
                        user_created = True
                    iterations -= 1
            if not user:
                res_dt['error'] = True
                res_dt['error_msg'] = 'Failed to create user, please contact administrator.'

            else:
                user_prof = LugatiUserProfile.objects.get(user=user)
                user_prof.company = LugatiCompany.objects.get(pk=object_dt['company'])
                from lugati.lugati_registration.models import LugatiRole
                user_prof.roles.add(LugatiRole.objects.get(name='waiter'))
                user_prof.save()

                # ~pre clerk
                # object_dt['user'] = user
                # todo!!!!
                from lugati.lugati_shop.forms import NgLugatiClerkForm
                form = NgLugatiClerkForm(request=request, data=object_dt)
                form.save()
                instance = form.instance
                instance.user = user
                instance.save()
                ms = form.cleaned_data['pic_array'].split(';')
                for img_id in ms:
                    if str(img_id).strip() <> '':
                        try:
                            tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                            tb_image.content_object = form.instance
                            tb_image.save()
                        except Exception, e:
                            logger.info('image not  saved:' + str(e))

        elif model_class.__name__ == 'LugatiTextBlock':
            from lugati.lugati_widgets.forms import NgLugatiTextBlockForm
            object_dt = json.loads(request.body)
            form = NgLugatiTextBlockForm(data=object_dt)
            form.save()

        elif model_class.__name__ == 'SalesPoint':
            from lugati.lugati_points_of_sale.forms import NgPosForm
            object_dt = json.loads(request.body)
            form = NgPosForm(site=cur_site, data=object_dt)
            form.save()

        elif model_class.__name__ == 'ShoppingPlace':

            from lugati.lugati_shop.forms import NgShoppingPlaceForm
            object_dt = json.loads(request.body)

            object_dt['bottom_title'] = '<b>' + object_dt['name'] + '</b>'
            object_dt['top_title'] = '<b>' + 'Scan me!' + '</b>'

            form = NgShoppingPlaceForm(request=request, data=object_dt)
            form.save()

        elif model_class.__name__ == 'LugatiPoem':
            from lugati.lugati_widgets.forms import NgLugatiPoemForm
            object_dt = json.loads(request.body)
            form = NgLugatiPoemForm(data=object_dt)
            obj = form.save()
            ms = form.cleaned_data['pic_array'].split(';')
            for img_id in ms:
                if str(img_id).strip() <> '':
                    try:
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()
                    except Exception, e:
                        logger.info('image not  saved:' + str(e))

        elif model_class.__name__ == 'LugatiPortfolioItem':

            from lugati.lugati_widgets.forms import NgLugatiPortfolioItemForm
            object_dt = json.loads(request.body)
            form = NgLugatiPortfolioItemForm(data=object_dt)
            obj = form.save()
            ms = form.cleaned_data['pic_array'].split(';')

            for img_id in ms:
                if str(img_id).strip() <> '':
                    try:
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()
                    except Exception, e:
                        logger.info('image not  saved:' + str(e))

        elif model_class.__name__ == 'LugatiNews':
            from lugati.lugati_widgets.forms import NgLugatiNewsForm
            object_dt = json.loads(request.body)
            form = NgLugatiNewsForm(data=object_dt)
            form.save()

        elif model_class.__name__ == 'DeliveryOption':
            from lugati.lugati_shop.lugati_delivery.forms import NgDeliveryOptionForm
            object_dt = json.loads(request.body)
            form = NgDeliveryOptionForm(request=request, data=object_dt)
            form.save()

        elif model_class.__name__ == 'DeliveryPrice':
            from lugati.lugati_shop.lugati_delivery.forms import NgDeliveryPriceForm
            object_dt = json.loads(request.body)
            form = NgDeliveryPriceForm(request=request, data=object_dt)
            form.save()

        elif model_class.__name__ == 'Product':
            from lugati.products.forms import NgProductForm, NgCategoryForm, NgToppingForm
            product_dt = json.loads(request.body)
            if not 'site' in product_dt:
                product_dt['site'] = cur_site.id
            product_dt['company'] = LugatiUserProfile.objects.get(user=request.user).get_company().id
            # product_dt['price_wo_discount'] = 0
            if (product_dt['is_category'] == 'True') or (product_dt['is_category'] == True):

                form = NgCategoryForm(request=request, data=product_dt)
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
                        form = NgToppingForm(request=request, data=product_dt)
                        obj = Product()
                        obj.company = LugatiCompany.objects.get(pk=product_dt['company'])
                        obj.site = cur_site
                        obj.is_category = product_dt['is_category']
                        obj.is_topping = product_dt['is_topping']
                        obj.price = product_dt['price']
                        obj.name = product_dt['name']
                        obj.styled_name = product_dt['name']
                        if product_dt['parent_object']:
                            obj.parent_object = Product.objects.get(pk=product_dt['parent_object'])
                        obj.save()
                        return HttpResponse(json.dumps(obj.get_list_item_info(request)))

                form = NgProductForm(request=request, data=product_dt)
                obj = form.save()
                ms = form.cleaned_data['pic_array'].split(';')
                for img_id in ms:
                    if str(img_id).strip() <> '':
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()

            return HttpResponse(json.dumps(obj.get_list_item_info(request)))

        elif model_class.__name__ == 'ThebloqVideo':
            from lugati.lugati_media.forms import NgThebloqVideoForm
            object_dt = json.loads(request.body)
            form = NgThebloqVideoForm(data=object_dt)
            form.save()

        elif model_class.__name__ == 'City':
            from lugati.lugati_points_of_sale.forms import NgCityForm
            object_dt = json.loads(request.body)
            form = NgCityForm(site=cur_site, data=object_dt)
            form.save()

        elif model_class.__name__ == 'Shop':
            from lugati.lugati_shop.forms import NgShopForm
            object_dt = json.loads(request.body)
            form = NgShopForm(request=request, data=object_dt)
            form.save()

        elif model_class.__name__ == 'GalleryItem':
            from lugati.lugati_media.lugati_gallery.forms import NgGalleryItemForm
            object_dt = json.loads(request.body)
            form = NgGalleryItemForm(request=request, data=object_dt)
            form.save()

        return HttpResponse(json.dumps(res_dt))

    elif request.method == 'PUT':
        res_dt = {}
        if model_class.__name__ == 'FlatPage':
            from lugati.lugati_static.views import LugatiFlatPageUpdateView
            lugatiView = LugatiFlatPageUpdateView.as_view()
            FPRes = lugatiView(request, url=object_id)
            return FPRes
            pass
        else:
            instance = model_class.objects.get(pk=object_id)


        can_edit = False
        if request.user.is_authenticated():
            object_dt = json.loads(request.body)
            if settings.SHOP_TYPE == "MPS":
                if hasattr(model_class, 'company'):
                    if instance.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                        can_edit = True
                    pass
                else:
                    if model_class.__name__ == 'LugatiCompany':
                        if instance == LugatiUserProfile.objects.get(user=request.user).get_company():
                            can_edit = True

                    elif model_class.__name__ == 'ShoppingPlace':
                        if instance.shop.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                            can_edit = True

                    elif model_class.__name__ == 'Tooltip':
                        can_edit = True

                    else:
                        pass
            else:
                #todo handle different sites
                can_edit = True
                # can_edit = False

        if not can_edit:
            #todo handle can't edit case
            pass
        elif model_class.__name__ == 'ProductPropertyValue':
            if settings.SHOP_TYPE == 'MPS':
                object_dt = json.loads(request.body)
                if 'default' in object_dt:
                    if object_dt['default']:
                        instance.default = object_dt['default']
                        instance.save()
                        prop_values = ProductPropertyValue.objects.filter(product_property=instance.product_property)
                        for prop_value in prop_values:
                            if prop_value <> instance:
                                if prop_value.default:
                                    prop_value.default = False
                                    # prop_value.save()
        #
        elif model_class.__name__ == 'LugatiClerk':
            from lugati.lugati_shop.forms import NgLugatiClerkForm
            form = NgLugatiClerkForm(request=request, data=object_dt, instance=instance)
            form.save()
            if 'pic_array' in object_dt:
                ms = object_dt['pic_array'].split(';')
                for img_id in ms:
                    if str(img_id).strip() <> '':
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = instance
                        tb_image.save()

        elif model_class.__name__ == 'LugatiTextBlock':
            from lugati.lugati_widgets.forms import NgLugatiTextBlockForm
            object_dt = json.loads(request.body)
            form = NgLugatiTextBlockForm(data=object_dt, instance=instance)
            form.save()

        elif model_class.__name__ == 'GalleryItem':
            from lugati.lugati_media.lugati_gallery.forms import NgGalleryItemForm
            object_dt = json.loads(request.body)
            form = NgGalleryItemForm(request=request, data=object_dt, instance=instance)
            obj = form.save()
            ms = form.cleaned_data['pic_array'].split(';')
            for img_id in ms:
                if str(img_id).strip() <> '':
                    try:
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()
                    except Exception, e:
                        logger.info('image not  saved:' + str(e))

        elif model_class.__name__ == 'Product':
            from lugati.products.forms import NgProductForm, NgCategoryForm


            # object_dt = json.loads(request.body)
            object_dt['site'] = cur_site.id
            if settings.SHOP_TYPE == 'MPS':
                if 'is_topping' in object_dt:
                    if object_dt['is_topping']:
                        from lugati.products.forms import NgToppingForm
                        if 'name' not in object_dt:
                            object_dt['name'] = instance.name
                        if instance.parent_object:
                            if not 'parent_object' in object_dt:
                                object_dt['parent_object'] = instance.parent_object.id
                        if 'in_stock' not in object_dt:
                            object_dt['in_stock'] = instance.in_stock
                        form = NgToppingForm(request=request, data=object_dt, instance=instance)
                        obj = form.save()

                        # todo
                        if 'price' in object_dt:
                            obj.price = object_dt['price']
                            obj.save()

                        if 'assigned_to_id' in object_dt:
                            try:
                                prod = Product.objects.get(pk = object_dt['assigned_to_id'])
                                if object_dt['active_topping']:
                                    obj.assigned_to.add(prod)
                                else:
                                    obj.assigned_to.remove(prod)
                            except Exception, e:
                                pass
                        # a1.publications.add(p1)
                        return HttpResponse(json.dumps(obj.get_list_item_info(request)))


                object_dt['company'] = LugatiUserProfile.objects.get(user=request.user).get_company().id
                if 'styled_name' in object_dt:
                    object_dt['name'] = strip_tags(object_dt['styled_name'])
                else:
                    if 'name' not in object_id:
                        object_dt['name'] = instance.name
                if 'styled_description' in object_dt:
                    object_dt['preview'] = strip_tags(object_dt['styled_description'])

            if instance.is_category:
                form = NgCategoryForm(request=request, data=object_dt, instance=instance)
            else:
                form = NgProductForm(request=request, data=object_dt, instance=instance)
            obj = form.save()
            if 'pic_array' in form.cleaned_data:
                ms = form.cleaned_data['pic_array'].split(';')
                for img_id in ms:
                    if str(img_id).strip() <> '':
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()

            if 'variations' in object_dt:
                def update_prop_values(prop, val, default=False):
                    try:
                        prop_value = ProductPropertyValue.objects.get(pk=val['id'])
                    except:
                        prop_value = ProductPropertyValue()

                    prop_value.product_property = prop

                    prop_value.value = val['value']
                    prop_value.name = val['name']
                    prop_value.default = val['default']

                    prop_value.save()

                    if 'price' in val:
                        #doing
                        try:
                            prod_price = ProductPrice.objects.get(product=prop.product, product_property_value=prop_value)
                        except:
                            prod_price = ProductPrice()
                            prod_price.product = prop.product
                            prod_price.product_property_value = prop_value
                        prod_price.price = val['price']
                        prod_price.save()

                if 'priceable' in object_dt['variations']:
                    if ProductProperty.objects.filter(product=instance, name='mps_priceable').exists():
                        prop = ProductProperty.objects.get(product=instance, name='mps_priceable')
                    else:
                        prop = ProductProperty()
                        prop.product = instance
                        prop.name = 'mps_priceable'
                        prop.save()

                    for var in object_dt['variations']['priceable']:
                        update_prop_values(prop, var)

                if 'not_priceable' in object_dt['variations']:
                    if ProductProperty.objects.filter(product=instance, name='mps_not_priceable').exists():
                        prop = ProductProperty.objects.get(product=instance, name='mps_not_priceable')
                    else:
                        prop = ProductProperty()
                        prop.product = instance
                        prop.name = 'mps_not_priceable'
                        prop.save()
                    for var in object_dt['variations']['not_priceable']:
                        update_prop_values(prop, var)

        elif model_class.__name__ == 'SalesPoint':
            from lugati.lugati_points_of_sale.forms import NgPosForm
            object_dt = json.loads(request.body)
            form = NgPosForm(site=cur_site, data=object_dt, instance=instance)
            form.save()
        elif model_class.__name__ == 'ShoppingPlace':
            from lugati.lugati_shop.forms import NgShoppingPlaceForm
            object_dt = json.loads(request.body)
            if 'bottom_title' in object_dt:
                new_name = strip_tags(object_dt['bottom_title'])
                if len(new_name)>50:
                    object_dt['name'] = new_name[0:46] + '...'
                elif len(new_name) == 0:
                    object_dt['name'] = instance.name
                else:
                    object_dt['name'] = new_name
            else:
                if not 'name' in object_dt:
                    object_dt['name'] = instance.name

            form = NgShoppingPlaceForm(request=request, data=object_dt, instance=instance)
            form.save()
        elif model_class.__name__ == 'LugatiDevice':
            from lugati.lugati_mobile.forms import NgLugatiDeviceForm
            object_dt = json.loads(request.body)
            form = NgLugatiDeviceForm(data=object_dt, instance=instance)
            form.save()

        elif model_class.__name__ == 'LugatiPoem':
            from lugati.lugati_widgets.forms import NgLugatiPoemForm
            object_dt = json.loads(request.body)
            form = NgLugatiPoemForm(data=object_dt, instance=instance)
            obj = form.save()
            ms = form.cleaned_data['pic_array'].split(';')
            for img_id in ms:
                if str(img_id).strip() <> '':
                    try:
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()
                    except Exception, e:
                        logger.info('image not  saved:' + str(e))

        elif model_class.__name__ == 'LugatiPortfolioItem':
            from lugati.lugati_widgets.forms import NgLugatiPortfolioItemForm
            object_dt = json.loads(request.body)
            form = NgLugatiPortfolioItemForm(data=object_dt, instance=instance)
            obj = form.save()
            ms = form.cleaned_data['pic_array'].split(';')
            for img_id in ms:
                if str(img_id).strip() <> '':
                    try:
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()
                    except Exception, e:
                        logger.info('image not  saved:' + str(e))

        elif model_class.__name__ == 'LugatiNews':
            from lugati.lugati_widgets.forms import NgLugatiNewsForm
            object_dt = json.loads(request.body)
            form = NgLugatiNewsForm(data=object_dt, instance=instance)
            form.save()

        elif model_class.__name__ == 'LugatiCompany':
            from lugati.lugati_shop.forms import NgLugatiCompanyForm
            object_dt = json.loads(request.body)
            form = NgLugatiCompanyForm(data=object_dt, instance=instance)
            obj = form.save()
            ms = object_dt['pic_array'].split(';')
            for img_id in ms:
                if str(img_id).strip() <> '':
                    try:
                        tb_image = ThebloqImage.objects.get(pk=str(img_id).strip())
                        tb_image.content_object = obj
                        tb_image.save()
                    except Exception, e:
                        logger.info('image not  saved:' + str(e))

        elif model_class.__name__ == 'DeliveryOption':
            from lugati.lugati_shop.lugati_delivery.forms import NgDeliveryOptionForm
            object_dt = json.loads(request.body)
            if object_dt['products'] == u'[]':
                object_dt['products'] = None
            form = NgDeliveryOptionForm(request=request, data=object_dt, instance=instance)
            form.save()
        elif model_class.__name__ == 'ThebloqVideo':
            from lugati.lugati_media.forms import NgThebloqVideoForm
            object_dt = json.loads(request.body)
            form = NgThebloqVideoForm(data=object_dt, instance=instance)
            form.save()
        elif model_class.__name__ == 'City':
            from lugati.lugati_points_of_sale.forms import NgCityForm
            object_dt = json.loads(request.body)
            object_dt['site'] = cur_site.id
            form = NgCityForm(site=cur_site, data=object_dt, instance=instance)
            form.save()
        elif model_class.__name__ == 'Shop':
            from lugati.lugati_shop.forms import NgShopForm
            object_dt = json.loads(request.body)
            form = NgShopForm(request=request,data=object_dt, instance=instance)
            form.save()
        elif model_class.__name__ == 'Order':
            from lugati.lugati_shop.lugati_orders.forms import LugatiOrderEditForm
            object_dt = json.loads(request.body)

            form = LugatiOrderEditForm(data=object_dt, instance=instance)
            form.save()
        elif model_class.__name__ == 'Tooltip':
            from lugati.lugati_admin.models import Tooltip, TooltipShow
            object_dt = json.loads(request.body)
            if (not object_dt['show']) and request.user.is_authenticated():
                tooltip_show = TooltipShow.objects.get(tooltip=Tooltip.objects.get(pk=object_dt['id']), user=request.user)
                tooltip_show.show = False
                tooltip_show.save()
            elif (object_dt['show']) and (request.user.is_authenticated()) and ('csrftoken' in object_dt) and ('show_in_session' in object_dt):
                tooltip_show = TooltipShow.objects.get(tooltip=Tooltip.objects.get(pk=object_dt['id']), user=request.user)
                tooltip_show.show_in_session = object_dt['show_in_session']
                tooltip_show.csrftoken = object_dt['csrftoken']
                tooltip_show.save()

        return HttpResponse(json.dumps(res_dt))
    elif request.method == 'DELETE':

        res_dt = {}

        obj = model_class.objects.get(pk=object_id)
        can_edit = False
        if request.user.is_authenticated():
            if settings.SHOP_TYPE == "MPS":
                if hasattr(model_class, 'company'):
                    if obj.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                        can_edit = True
                    pass
                else:
                    if model_class.__name__ == 'LugatiCompany':
                        if obj == LugatiUserProfile.objects.get(user=request.user).get_company():
                            can_edit = True
                        pass

                    elif model_class.__name__ == 'ShoppingPlace':
                        if obj.shop.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                            can_edit = True
                        pass
                    elif model_class.__name__ == 'ProductPropertyValue':
                        if obj.product_property.product.company == LugatiUserProfile.objects.get(user=request.user).get_company():
                            can_edit = True
                    else:
                        pass
            else:
                #todo handle different sites
                can_edit = True
                # can_edit = False

        if can_edit:
            obj.delete()

        return HttpResponse(json.dumps(res_dt))

def send_via_email(request, content_type_id, object_id):
    model_class = ContentType.objects.get(pk=content_type_id).model_class()
    if model_class.__name__ == "Order":
        instance = model_class.objects.get(pk=object_id)

        path = instance.get_pdf_order_path()
        email = request.GET['email']

        cur_context = {}
        cur_context['order'] = instance.get_list_item_info(request)
        if instance.shopping_place:
            cur_context['company'] = instance.shopping_place.shop.company
        message_html_t = get_template('lugati_admin/lugati_version_1_0/orders/mail_template.html')
        message_html = message_html_t.render(Context(cur_context))

        # return render(request, 'lugati_admin/lugati_version_1_0/orders/ng_order_details_template.html', resp_data)

        try:
            msg_text = 'Hello, here is the receipt'
            emails = [email]
            msg = EmailMultiAlternatives('Order ' + str(instance.id) + ' receipt', msg_text, settings.DEFAULT_FROM_EMAIL, emails)
            msg.attach_alternative(message_html, "text/html")
            msg.attach_file(path)

            msg.send()
        except Exception, e:
            # pass
            logger.info('send via email err: ' + str(e))

        return HttpResponse(json.dumps({}))
    else:
        return HttpResponse(json.dumps({}))

@csrf_exempt
def api_delete_object(request, content_type_id, object_id):
    model_class = ContentType.objects.get(pk=content_type_id).model_class()
    instance = model_class.objects.get(pk=object_id)
    try:
        instance.lugati_delete()
    except:
        instance.delete()
    return HttpResponse(json.dumps({}))

def lugati_content_type(request, id=''):
    res_dt = {}
    if request.method == 'GET':
        if id == '':
            res_dt = []
            node = {
                'id': ContentType.objects.get_for_model(Product).id,
                'name': ContentType.objects.get_for_model(Product).model_class().__name__,
                'hierarchical': True,
            }
            res_dt.append(node)
        else:
            if str(id) == str(ContentType.objects.get_for_model(Order).id):
                node = {
                    'id': ContentType.objects.get_for_model(Order).id,
                    'name': ContentType.objects.get_for_model(Order).model_class().__name__
                }
                node['hierarchical'] = lugati_procs.is_hierarchical(ContentType.objects.get_for_model(Order))
                node['has_map'] = lugati_procs.has_map(ContentType.objects.get_for_model(Order))
                node['has_images'] = lugati_procs.has_images(ContentType.objects.get_for_model(Order))
                node['can_create'] = lugati_procs.can_create(ContentType.objects.get_for_model(Order))
                node['can_delete'] = lugati_procs.can_delete(ContentType.objects.get_for_model(Order))
                node['is_periodic'] = True
                res_dt = node

            elif str(id).lower() == 'Product'.lower():
                node = {
                    'id': ContentType.objects.get_for_model(Product).id,
                    'name': ContentType.objects.get_for_model(Product).model_class().__name__
                }
                node['hierarchical'] = lugati_procs.is_hierarchical(ContentType.objects.get_for_model(Product))
                node['has_map'] = lugati_procs.has_map(ContentType.objects.get_for_model(Product))
                node['has_images'] = lugati_procs.has_images(ContentType.objects.get_for_model(Product))
                node['can_create'] = lugati_procs.can_create(ContentType.objects.get_for_model(Product))
                node['can_delete'] = lugati_procs.can_delete(ContentType.objects.get_for_model(Product))
                node['is_periodic'] = False
                res_dt = node

            elif str(id).lower() == 'LugatiTextBlock'.lower():
                from lugati.lugati_widgets.models import LugatiTextBlock
                node = {
                    'id': ContentType.objects.get_for_model(LugatiTextBlock).id,
                    'name': ContentType.objects.get_for_model(LugatiTextBlock).model_class().__name__
                }
                node['hierarchical'] = lugati_procs.is_hierarchical(ContentType.objects.get_for_model(LugatiTextBlock))
                node['has_map'] = lugati_procs.has_map(ContentType.objects.get_for_model(LugatiTextBlock))
                node['has_images'] = lugati_procs.has_images(ContentType.objects.get_for_model(LugatiTextBlock))
                node['can_create'] = lugati_procs.can_create(ContentType.objects.get_for_model(LugatiTextBlock))
                node['can_delete'] = lugati_procs.can_delete(ContentType.objects.get_for_model(LugatiTextBlock))
                node['is_periodic'] = False
                res_dt = node

            else:
                node = {
                    'id': ContentType.objects.get(pk=id).id,
                    'name': ContentType.objects.get(pk=id).model_class().__name__
                }
                node['hierarchical'] = lugati_procs.is_hierarchical(ContentType.objects.get(pk=id))
                node['has_map'] = lugati_procs.has_map(ContentType.objects.get(pk=id))
                node['has_images'] = lugati_procs.has_images(ContentType.objects.get(pk=id))
                node['can_create'] = lugati_procs.can_create(ContentType.objects.get(pk=id))
                node['can_delete'] = lugati_procs.can_delete(ContentType.objects.get(pk=id))
                node['is_periodic'] = False
                res_dt = node

    return HttpResponse(json.dumps(res_dt))

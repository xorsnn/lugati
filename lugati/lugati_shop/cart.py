
from .lugati_cart.models import CartItem, CartDelivery, CartItemOption
#from .lugati_cart.models import CartDelivery
from lugati.lugati_shop.lugati_delivery.models import DeliveryOption, DeliveryPrice

from lugati.products.models import Product, ProductPropertyValue
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from lugati.lugati_shop.models import ShoppingPlace
from django.core.urlresolvers import resolve
from lugati.lugati_shop.lugati_orders.models import Order, OrderItem, OrderItemOption

import decimal
import random
import json
CART_ID_SESSION_KEY = 'cart_id'
# get the current user's cart id, sets new one if blank
def _cart_id(request):
    cart_id_pref = ''
    try:
        cart_id_pref = resolve(request.GET['cur_path']).kwargs['pos_id']
    except:
        pass

    if cart_id_pref == '':
        try:
            cart_id_pref = resolve(request.POST['cur_path']).kwargs['pos_id']
        except:
            pass

    if cart_id_pref == '':
        try:
            cart_id_pref = resolve(json.loads(request.POST)['cur_path']).kwargs['pos_id']
        except:
            pass
    if request.user.is_authenticated():
        # if request.session.get(CART_ID_SESSION_KEY,'') == '':
        request.session[CART_ID_SESSION_KEY] = cart_id_pref + '_' + request.user.username + '_' + str(request.user.id)
    else:
        if request.session.get(CART_ID_SESSION_KEY, '') == '':
            request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
        return cart_id_pref + '_' + request.session[CART_ID_SESSION_KEY]
    return request.session[CART_ID_SESSION_KEY]
def _generate_cart_id():
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 50
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id
# return all items from the current user's cart
def get_cart_items(request):
    return CartItem.objects.filter(cart_id=_cart_id(request))

def get_cart_items_with_toppings(request):
    return CartItem.objects.filter(cart_id=_cart_id(request)).filter(cart_item_assigned=None)

def get_all_cart_delivery(request):
   return CartDelivery.objects.filter(cart_id=_cart_id(request))

def add_delivery_option(request, delivery_option):
   cart_delivery = CartDelivery()
   cart_delivery.cart_id = _cart_id(request)
   cart_delivery.delivery_option = delivery_option
   cart_delivery.save()

# add an item to the cart

def remove_product_from_cart(request):
    res_cart_item = None
    postdata = request.POST.copy()
    prod_id = postdata['prod_id']
    cart_products = get_cart_items(request)

    for cart_item in cart_products:
        if str(cart_item.product.id) == str(prod_id):
            if cart_item.quantity <= 1:
                cart_item.delete()
                res_cart_item = None
            else:
                cart_item.augment_quantity(-1)
                res_cart_item = cart_item
    return res_cart_item

def add_product_to_cart(request, prod_id=None, quantity=None, pos_id=None, options=None, cart_item_assigned=None):

    res_cart_item = None

    if (prod_id == None) and (quantity == None):
        postdata = request.POST.copy()
        prod_id = postdata['prod_id']
        quantity = postdata['quantity']

    # fetch the product or return a missing page error
    p = get_object_or_404(Product, id=prod_id)

    #get products in cart
    cart_products = get_cart_items(request)
    product_in_cart = False

    # check to see if item is already in cart
    def get_cart_item_options_id_str(item):
        item_options = CartItemOption.objects.filter(cart_item=item).values_list('product_option', flat=True).order_by('-product_option')
        return ';'.join([str(item_option_id) for item_option_id in item_options])

    # todo!!!
    def get_options_id_arr(options):
        if options:
            opt_id_arr = []
            if 'priceable' in options:
                for opt in options['priceable']:
                    if opt['active']:
                        opt_id_arr.append(opt['id'])
            if 'not_priceable' in options:
                for opt in options['not_priceable']:
                    if opt['active']:
                        opt_id_arr.append(opt['id'])
            res = sorted(opt_id_arr)
        else:
            res = []
        return res

    def get_options_id_str(options_id_arr):
        return ';'.join([str(item_option_id) for item_option_id in options_id_arr])

    # todo!!
    if False:
        for cart_item in cart_products:
            if (cart_item.product.id == p.id) \
                    and (get_cart_item_options_id_str(cart_item) == get_options_id_str(get_options_id_arr(options))):
                if cart_item_assigned:
                    if (cart_item.cart_item_assigned.id == cart_item_assigned):
                        # pass
                        product_in_cart = True
                else:
                    if not cart_item.get_toppings().exists():
                        # pass
                        product_in_cart = True

                if product_in_cart:
                    # update the quantity if found
                    res_cart_item = cart_item
                    cart_item.augment_quantity(quantity)

    # todo !!!!
    # product_in_cart = False

    if not product_in_cart:
        # create and save a new cart item
        ci = CartItem()
        if (cart_item_assigned):
            item_assigned = CartItem.objects.get(pk=cart_item_assigned)
            ci.cart_item_assigned = item_assigned
            ci.quantity = item_assigned.quantity
        else:
            ci.quantity = quantity
        ci.product = p
        ci.cart_id = _cart_id(request)

        if pos_id:
            try:
                cur_shopping_place = ShoppingPlace.objects.get(pk=pos_id)
            except:
                cur_shopping_place = None
        else:
            try:
                cur_shopping_place = ShoppingPlace.objects.get(pk=resolve(request.POST['cur_url']).kwargs['pos_id'])
            except:
                cur_shopping_place = None


        if cur_shopping_place:
            ci.shopping_place = cur_shopping_place

        ci.save()

        # adding options
        if (options):
            opts = get_options_id_arr(options)
            for opt in opts:
                #todo second cart item save
                prop_val = ProductPropertyValue.objects.get(pk=opt)
                if prop_val.product_property.name == 'mps_priceable':
                    ci.price = ci.product.get_price(prop_val)
                    ci.save()
                cart_item_option = CartItemOption()
                cart_item_option.cart_item = ci
                cart_item_option.product_option = prop_val
                cart_item_option.save()

        res_cart_item = ci

    return res_cart_item

# returns the total number of items in the user's cart
def cart_distinct_item_count(request):
    return get_cart_items(request).count()

def get_total_delivery_price(request):
    cart_items = get_cart_items(request)
    total_delivery_price = decimal.Decimal(0)
    delivery_cart_options = get_all_cart_delivery(request)

    if delivery_cart_options.exists():
        # total_delivery_cost = decidel_price = DeliveryPrice.objects.get(delivmal.Decimal(0)
        # total_delivery_additional_cost = decimal.Decimal(0)

        delivery_option = delivery_cart_options[0].delivery_option
        del_prices = []

        largest_price = 0
        for cart_item in cart_items:

            try:
                del_price = DeliveryPrice.objects.get(delivery_option=delivery_option, product=cart_item.product)
                if del_price.price > largest_price:
                    largest_price = del_price.price
                del_prices.append({
                    'price': del_price.price,
                    'additional_price': del_price.additional_price,
                    'quantity': cart_item.quantity,
                    'largest': False
                })

            except:
                pass

        for price in del_prices:
            if largest_price == price['price']:
                price['largest'] = True
                break

        total_delivery_price = 0
        for price in del_prices:
            if price['largest']:
                total_delivery_price += price['price']
                price['quantity'] -= 1
            total_delivery_price += (price['quantity'] * price['additional_price'])

    return total_delivery_price


def make_order_paid(cart_id):
    # logger.info('trying body')
    cart_items = CartItem.objects.filter(cart_id=cart_id).filter(cart_item_assigned=None)
    # try:
    sum = 0

    for cart_item in cart_items:
        sum += cart_item.total()
        #todo !!!
        cur_site = cart_item.product.site
    # logger.info('total sum -> ' + str(sum))
    order = None
    if cart_items.count() > 0:
        order = Order()
        order.site = cur_site
        #todo !!!!!
        order.cart_id = cart_items[0].cart_id
        order.shopping_place = cart_items[0].shopping_place
        #~!!!!!
        order.save()

        for cart_item in cart_items:
            order_item = OrderItem()
            order_item.order = order
            order_item.quantity = cart_item.quantity
            order_item.product = cart_item.product
            order_item.price = cart_item.get_price()#!!!!
            order_item.save()
            # copy it to payment
            for cart_item_option in CartItemOption.objects.filter(cart_item=cart_item):
                order_item_option = OrderItemOption()
                order_item_option.order_item = order_item
                order_item_option.product_option = cart_item_option.product_option
                order_item_option.save()
            # ~copy it to payment
            for topping in cart_item.get_toppings():
                topping_order_item = OrderItem()
                topping_order_item.order = order
                topping_order_item.quantity = topping.quantity
                topping_order_item.product = topping.product
                topping_order_item.price = topping.get_price()#!!!!
                topping_order_item.item_assigned = order_item
                topping_order_item.save()

            # logger.info('added -> ' + cart_item.product.name + ' ' + str(cart_item.quantity))
            cart_item.delete()
    return order

    #         logger.info('devices' + '1')
    #         clerks = LugatiClerk.objects.filter(company=order.shopping_place.shop.company)
    #         for clerk in clerks:
    #             try:
    #                 logger.info('trying sending notification')
    #                 data = {
    #                     'title': order.shopping_place.shop.company.name,
    #                     'message': "order " + str(order.id) + " paid (" + str(order.shopping_place) + ")",
    #                     'timeStamp': datetime.datetime.now().isoformat(),
    #                     'type': 'new_order',
    #                     'order_id': str(order.id)
    #                 }
    #                 gcm.plaintext_request(registration_id=clerk.reg_id, data=data)
    #             except Exception, e:
    #                 logger.info('exception: ' + str(e))
    #
    #     # stomp!!!
    #     stomp_conn.send(body=json.dumps({'message': 'order_paid', 'order': order.get_list_item_info()}), destination='/topic/' + 'payment_channel_' + str(LugatiShoppingSession.objects.filter(cart_id=cart_id)[0].id))
    #
    #
    # except Exception, e:
    #     logger.info('err -> ' + str(e))
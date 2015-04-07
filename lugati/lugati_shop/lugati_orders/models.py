# -*- coding: utf-8 -*-
from django.db import models
from lugati.products.models import Product
from django.db.models import Max
from django.contrib.sites.models import Site
from lugati.lugati_shop.models import ShoppingPlace
from django.utils import dateformat
from django.conf import settings
from lugati.lugati_shop.lugati_delivery.models import City, DeliveryOption
import json
from lugati.lugati_shop.models import LugatiShoppingSession
from django.core.urlresolvers import resolve
from reportlab.pdfgen import canvas
from django.contrib.contenttypes.models import ContentType
from lugati.lugati_registration.models import LugatiUserProfile
import stomp

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from lugati.lugati_shop.models import LugatiClerk
from lugati.products.models import ProductPropertyValue
import stomp


stomp_conn = stomp.Connection()
stomp_conn.start()
stomp_conn.connect()

def get_default_state():
    try:
        return OrderState.objects.get(name='PAID', custom_id=1)
    except:
        return None

class OrderState(models.Model):
    name = models.CharField(max_length=50)
    custom_id = models.IntegerField(default=0)
    site = models.ForeignKey(Site, blank=True, null=True)
    class_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Order(models.Model):
    # order_num = models.IntegerField(unique=True)
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    cart_id = models.CharField(max_length=60,  blank=True, null=True)
    site = models.ForeignKey(Site)
    state = models.ForeignKey(OrderState, default=get_default_state)
    dt_modify = models.DateTimeField(auto_now=True)
    dt_add = models.DateTimeField(auto_now_add=True, editable=False)

    clerk = models.ForeignKey(LugatiClerk, null=True, blank=True)

    delivery_price = models.DecimalField(default=0, max_digits=15, decimal_places=8, null=True, blank=True)
    shopping_place = models.ForeignKey(ShoppingPlace, blank=True, null=True)

    #additional client fields
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    delivery_option = models.ForeignKey(DeliveryOption, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    zip_code = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    tracking_number = models.CharField(max_length=200, null=True, blank=True)

    receipt_path = models.CharField(max_length=500, blank=True, null=True)



    class Meta:
        ordering = ['-dt_add']

    def get_shopping_session_id(self):
        try:
            shopping_session = LugatiShoppingSession.objects.get(cart_id=self.cart_id)
        except:
            shopping_session = LugatiShoppingSession()
            shopping_session.cart_id = self.cart_id
            shopping_session.company = self.shopping_place.shop.company
            shopping_session.save()
        return shopping_session.id



    def get_local_pdf_order_path(self):
        return settings.STATIC_ROOT + '/' + self.get_pdf_order_path().replace(settings.MEDIA_URL, '')

    def get_pdf_order_path(self):
        offset_y = 0
        delta_y = 20
        width = 294
        delimiter = '--------------------------------------'
        delimiter_s = '--------------------------------'

        def split_by_rows(name_str, row_length):
            res = []
            cur_row = ''
            words = name_str.split(' ')
            for word in words:
                if len(cur_row + ' ' + word.strip()) > row_length:
                    res.append(cur_row)
                    cur_row = word.strip()
                else:
                    cur_row += ' ' + word.strip()
            if cur_row <> '':
                res.append(cur_row)
            return res

        ord_items = []
        prod_rows_count = 0

        for item in self.get_items():
            name_arr = split_by_rows(item.product.name, len(delimiter_s))
            ord_items.append({
                'name_arr': name_arr,
                'price': item.total(),
                'quantity': item.quantity
            })
            prod_rows_count += len(name_arr)


        default_row_count = 7
        if self.shopping_place:
            default_row_count += 1
            # contact_data
            cur_company = self.shopping_place.shop.company
            if cur_company.phone:
                default_row_count += 1
            if cur_company.email:
                default_row_count += 1
            if cur_company.website_link:
                default_row_count += 1
            if cur_company.address:
                address_rows = split_by_rows(cur_company.address, len(delimiter_s)-6)
                default_row_count += len(address_rows)



        height = default_row_count*delta_y + prod_rows_count*delta_y + 100

        top_y = height - 50

# real print
        relative_path = 'upload/receipt_' + str(self.id) + '.pdf'
        receipt_path = settings.MEDIA_ROOT + relative_path
        p = canvas.Canvas(receipt_path)
        p.setPageSize((width, height))

        pdfmetrics.registerFont(TTFont('LugatiCourier', settings.MEDIA_ROOT+'fonts/courier.ttf'))

        # p.addFont('TestFont')
        p.setFont('LugatiCourier', 12)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        order = self

        # header

        top_x = 10
        # delta_x = 100

        p.drawString(top_x, top_y-offset_y, "Order number: " + str(order.id))
        offset_y += delta_y
        p.drawString(top_x, top_y-offset_y, "Order date: " + str(order.get_dt()))

        if order.shopping_place:
            offset_y += delta_y
            p.drawString(top_x, top_y-offset_y, "Ordering place: " + unicode(order.shopping_place.name))
            # p.drawString(top_x+delta_x, top_y-offset_y, unicode(order.shopping_place.name))
        # todo!!!
        offset_y += delta_y
        p.drawString(top_x, top_y-offset_y, "Waiter: " + unicode('Luigi'))
        # ~todo

        offset_y += delta_y
        offset_y += delta_y



        # body
        p.drawString(top_x, top_y-offset_y, delimiter)

        offset_y += delta_y
        # offset_y += delta_y

        col_1_w = 20
        col_2_w = 200
        col_3_w = 20

        ind = 1

        for item in ord_items:
            # amount:
            iteration = 1
            for name_str in item['name_arr']:
                if iteration == 1:
                    p.drawString(top_x, top_y-offset_y, str(item['quantity']))
                    p.drawString(top_x+col_1_w, top_y-offset_y, unicode(name_str))
                    p.drawString(top_x+col_1_w+col_2_w+col_3_w, top_y-offset_y, str('%.2f' % item['price']))
                    offset_y += delta_y
                    iteration += 1
                else:
                    p.drawString(top_x+col_1_w, top_y-offset_y, unicode(name_str))
                    offset_y += delta_y
            ind += 1

        # footer
        # offset_y += delta_y
        p.drawString(top_x, top_y-offset_y, delimiter)
        offset_y += delta_y
        p.drawString(top_x, top_y-offset_y, 'Total:')
        p.drawString(top_x+col_1_w+col_2_w+col_3_w, top_y-offset_y, str('%.2f' % order.get_total_sum()))
        offset_y += delta_y

        # contact data
        offset_y += delta_y
        p.drawString(top_x + ((len(delimiter)-len(cur_company.name.strip()))/2*7), top_y-offset_y, cur_company.name.strip())
        if order.shopping_place:
            cur_company = order.shopping_place.shop.company
            if cur_company.phone:
                offset_y += delta_y
                p.drawString(top_x, top_y-offset_y, "Phone: " + cur_company.phone)
            if cur_company.email:
                offset_y += delta_y
                p.drawString(top_x, top_y-offset_y, "Email: " + cur_company.email)
            if cur_company.website_link:
                offset_y += delta_y
                p.drawString(top_x, top_y-offset_y, "Website: " + cur_company.website_link)
            if cur_company.address:
                iteration = 1
                for row in address_rows:
                    offset_y += delta_y
                    if iteration == 1:
                        p.drawString(top_x, top_y-offset_y, "Address: " + row.strip())
                        iteration += 1
                    else:
                        p.drawString(top_x + 65, top_y-offset_y, row.strip())

        p.showPage()
        p.save()


        return receipt_path

    def save(self, *args, **kwargs):

        super(Order, self).save(*args, **kwargs)

        if settings.HAS_NOTIFICATION_SERVER:

            # stomp_conn.send(body=(json.dumps(self.get_list_item_info())), destination='/topic/orders')
            stomp_conn.send(body=(json.dumps(self.get_list_item_info())), destination='/topic/order_' + str(self.id))
            stomp_conn.send(body=(json.dumps(self.get_list_item_info())), destination='/topic/company_orders_' + str(self.shopping_place.shop.company.id))
            stomp_conn.send(body=(json.dumps(self.get_list_item_info())), destination='/topic/client_orders_' + str(LugatiShoppingSession.objects.get(pk=self.get_shopping_session_id()).id))

    def get_avaliable_states(self):

        res = {}
        for order_state in OrderState.objects.all():
            res[str(order_state.id)] = {
                'id': order_state.id,
                'name': order_state.name
            }
            if (order_state.name == 'CANCELLED&REFUNDED'):
                res[str(order_state.id)]['preview_name'] = 'CANCEL'
            else:
                res[str(order_state.id)]['preview_name'] = order_state.name
        return res

    def get_avaliable_states_array(self):

        from lugati.lugati_shop.lugati_orders.models import OrderState
        res = []
        for order_state in OrderState.objects.all():
            if (order_state.name == 'CANCELLED&REFUNDED'):
                preview_name = 'CANCEL'
            else:
                preview_name = order_state.name
            res.append({
                'id': order_state.id,
                'name': order_state.name,
                'preview_name': preview_name
            })
        return res

    def get_list_item_info(self, request=None, cur_company=None, export=False):

        res = {
            'id': self.id,
            'name': self.get_preview(),
            'details_url': 'edit' + '/' + str(ContentType.objects.get_for_model(Order).id) + '/' + str(self.id) + '/',
            'preview': self.get_preview(),
            'order_date': self.get_dt(),
            'paid': str(self.paid),
            'delivered': str(self.delivered),
            'cart_id': str(self.cart_id),
            'site': self.site.id,
            'state': self.state.id,
            'state_name': self.state.name,
            'avaliable_states': self.get_avaliable_states(),
            'avaliable_states_arr': self.get_avaliable_states_array(),
            'dt_modify': str(self.dt_modify),
            'dt_add': str(self.dt_add),
            'delivery_price': str(self.delivery_price),
            'place': '',
            'class': str(self.state.class_name),
            'css_ng_class': str(self.state.class_name),
            'total_sum': '%.2f' % self.get_total_sum(),
            'receipt_path': '/catalog/lugati_orders/pdf_receipt/' + str(self.id) + '/',
            # 'receipt_path': self.get_pdf_order_path(),
            'order_items': []
        }

        if self.clerk:
            res['waiter'] = str(self.clerk)
        else:
            res['waiter'] = 'unassigned'


        if self.shopping_place:
            res['shopping_place'] = self.shopping_place.id
            res['place'] = self.shopping_place.name
            res['currency_icon_class'] = self.shopping_place.shop.company.default_currency.icon_class_name

        elif request:
            if request.user.is_authenticated():
                prof = LugatiUserProfile.objects.get(user=request.user)
                res['currency_icon_class'] = prof.get_company().default_currency.icon_class_name
            elif 'cur_path' in request.GET:
                resolved_path = resolve(request.GET['cur_path'])
                pos_id = resolved_path.kwargs['pos_id']
                place = ShoppingPlace.objects.get(pk=pos_id)
                cur_company = place.shop.company
                res['currency_icon_class'] = cur_company.default_currency.icon_class_name

        order_items = self.orderitem_set.filter(item_assigned=None)
        for order_item in order_items:
            order_item_dt = order_item.get_list_item_info(request)
            toppings = self.orderitem_set.filter(item_assigned=order_item)
            if (toppings.exists()):
                order_item_dt['toppings'] = []
            for topping in toppings:
                order_item_dt['toppings'].append(topping.get_list_item_info(request))
            res['order_items'].append(order_item_dt)
        return res

    def get_new_order_number(self):
        max_num = Order.objects.all().aggregate(Max('order_num'))
        if max_num['order_num__max']:
            return max_num['order_num__max'] + 1
        else:
            return 1

    def get_preview(self):
        return '№' + str(self.id) + ' ' + self.dt_add.strftime('%d %b %Y %H:%M:%S') + ' ' + str(self.shopping_place) + ' (' + ('%.2f' % self.get_total_sum()) + ')'

    def get_dt(self):
        return self.dt_add.strftime('%d %b %Y %H:%M:%S')

    def get_total_sum(self):
        order_items = self.orderitem_set.all()
        total = 0
        for order_item in order_items:
            total += order_item.get_total_price()
        return total

    def get_items(self):
        return self.orderitem_set.all()


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey(Product, unique=False)
    price = models.FloatField(default=0)
    item_assigned = models.ForeignKey('self', blank=True, null=True)

    def get_list_item_info(self, request=None, cur_company=None):
        res = {
            'id': self.id,
            'content_object_id': ContentType.objects.get_for_model(OrderItem).id,
            'prod_id': self.product.id,
            'name': self.product.name,
            'quantity': self.quantity,
            'price': '%.2f' % self.price,
            'total': '%.2f' % self.get_total_price()
        }
        #todo
        res['options'] = {
            'priceable': [],
            'not_priceable': []
        }

        for opt in self.orderitemoption_set.all():
            list_item_info = opt.product_option.get_list_item_info()
            if ('priceable' in list_item_info):
                if (list_item_info['priceable']):
                    res['options']['priceable'].append(list_item_info)
                else:
                    res['options']['not_priceable'].append(list_item_info)
        #~todo

        res['thumbnail'] = self.product.get_thumbnail()

        if request:
            if request.user.is_authenticated():
                prof = LugatiUserProfile.objects.get(user=request.user)
                res['currency_icon_class'] = prof.get_company().default_currency.icon_class_name
            elif 'cur_path' in request.GET:
                resolved_path = resolve(request.GET['cur_path'])
                pos_id = resolved_path.kwargs['pos_id']
                place = ShoppingPlace.objects.get(pk=pos_id)
                cur_company = place.shop.company
                res['currency_icon_class'] = cur_company.default_currency.icon_class_name
        return res

    def get_thumbnail_url(self):
        return self.product.get_thumbnail()['image_url']

    def save(self, *args, **kwargs):
        super(OrderItem, self).save(*args, **kwargs)

        if settings.HAS_NOTIFICATION_SERVER:

            try:
                session = LugatiShoppingSession.objects.get(cart_id=self.order.cart_id)
                c.publish('client_channel_' + str(session.id), json.dumps({'message':'order_updated','order': self.order.get_list_item_info()}))
            except Exception, e:
                pass

            # stopm
            stomp_conn.send(body=(json.dumps(self.order.get_list_item_info())), destination='/topic/order_' + str(self.order.id))
            stomp_conn.send(body=(json.dumps(self.order.get_list_item_info())), destination='/topic/company_orders_' + str(self.order.shopping_place.shop.company.id))
            stomp_conn.send(body=(json.dumps(self.order.get_list_item_info())), destination='/topic/client_orders_' + str(LugatiShoppingSession.objects.get(pk=self.order.get_shopping_session_id()).id))

    def get_total_price(self):
        return self.quantity*self.price

    def total(self):
        return self.quantity*self.price

class OrderItemOption(models.Model):
    order_item = models.ForeignKey(OrderItem)
    product_option = models.ForeignKey(ProductPropertyValue)
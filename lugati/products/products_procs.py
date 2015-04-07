from lugati.lugati_registration.models import LugatiUserProfile
import json
from lugati.products.models import Product, ProductPrice, Brand
import json
from django.core.files import File
from django.contrib.sites.models import Site
import cStringIO
from PIL import Image
from lugati.lugati_media.models import ThebloqImage
from django.core.files.uploadedfile import InMemoryUploadedFile
import StringIO
import datetime
from lugati.lugati_shop.lugati_orders.models import Order, OrderItem
from lugati.lugati_shop.models import ShoppingPlace, Shop
import random
from django.db import connection

def create_demo_account(site_id, user):

    # prof = LugatiUserProfile.objects.get(user=user)
    # Order.objects.filter(site=Site.objects.get(pk=site_id)).delete()
    # Product.objects.filter(site=site_id).delete()
    # ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=prof.get_company())).delete()

    generate_order_points(site_id, user)
    load_demo_data(site_id, user)
    generate_week_sales(site_id, user)

def generate_order_points(site_id, user, amount=5):
    prof = LugatiUserProfile.objects.get(user=user)
    shop = Shop.objects.filter(company=prof.get_company())[0]
    for i in range(1, amount+1):
        sh_place = ShoppingPlace()
        sh_place.name = 'table_' + str(i)
        sh_place.shop = shop
        sh_place.save()

def load_demo_data(site_id, user):
    file = open('export.json', 'r')
    str = file.read()
    res = json.loads(str)
    def rec_proc(ms, parent=None):
        for prod in ms:
            new_prod = Product()
            new_prod.code = prod['code']
            new_prod.sku = prod['sku']
            new_prod.name = prod['name']
            new_prod.styled_name = prod['name']
            new_prod.description = prod['description']
            new_prod.styled_description = prod['description']
            new_prod.preview = prod['preview']
            new_prod.is_category = prod['is_category']
            new_prod.active = prod['active']
            new_prod.priority = prod['priority']
            # ????
            new_prod.site = Site.objects.get(pk=site_id)
            new_prod.additional_info = prod['additional_info']
            new_prod.in_stock = prod['in_stock']
            new_prod.price_wo_discount = float(prod['price_wo_discount'])
            new_prod.price = float(prod['price'])
            new_prod.parent_object = parent

            #to company
            new_prod.company = LugatiUserProfile.objects.get(user=user).get_company()
            new_prod.save()
            for img in prod['images']:
                file_like = cStringIO.StringIO(img.decode('base64'))
                img = Image.open(file_like)

                tempfile_io = StringIO.StringIO()
                img.save(tempfile_io, format='PNG')

                tb_image = ThebloqImage()
                tb_image.file = InMemoryUploadedFile(tempfile_io, None, 'prod_img.png', 'image/png', tempfile_io.len, None)
                tb_image.content_object = new_prod
                tb_image.save()

            print prod['name']
            rec_proc(prod['children'], new_prod)
    rec_proc(res)

def generate_week_sales(site_id, user):
    HISTORY_LENGTH = 7
    prof = LugatiUserProfile.objects.get(user=user)

    day_delta = datetime.timedelta(days=1)

    now = datetime.datetime.now()
    cur_day = datetime.datetime(now.year, now.month, now.day)

    for i in range(HISTORY_LENGTH):
        print 'day: ' + str(i)
        for b in range(5):
            new_order = Order()
            new_order.date = cur_day
            new_order.cart_id = '1'
            new_order.site = Site.objects.get(pk=site_id)
            new_order.dt_modify = cur_day
            new_order.dt_add = cur_day
            new_order.shopping_place = get_shopping_place(user)
            new_order.save()
            cursor = connection.cursor()

            cursor.execute("UPDATE lugati_orders_order SET dt_add = %s, dt_modify= %s, date= %s WHERE id = %s", [str(cur_day), str(cur_day), str(cur_day), new_order.id])

            num_of_items = random.randint(1, 4)
            for item_num in range(num_of_items):
                new_order_item = OrderItem()
                new_order_item.product = get_random_product(user)
                new_order_item.quantity = random.randint(1, 3)
                new_order_item.order = new_order
                new_order_item.price = float(random.randint(100, 1000))/10
                new_order_item.save()
        cur_day = cur_day - day_delta

def get_random_product(user):
    prof = LugatiUserProfile.objects.get(user=user)
    products = Product.objects.filter(company = prof.get_company()).filter(is_category = False)
    prod_ind = random.randint(0, products.count()-1)
    return products[prod_ind]

def get_shopping_place(user):
    prof = LugatiUserProfile.objects.get(user=user)
    places = ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=prof.get_company()))
    place_ind = random.randint(0, places.count()-1)
    return places[place_ind]
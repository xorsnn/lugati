from django.db import models
from lugati.products.models import Product, ProductPropertyValue, ProductProperty
from lugati.lugati_shop.models import ShoppingPlace
from lugati.lugati_shop.lugati_delivery.models import DeliveryOption
from django.core.urlresolvers import resolve
from lugati.lugati_media.models import ThebloqImage
from django.contrib.contenttypes.models import ContentType

class CartItem(models.Model):
    cart_id = models.CharField(max_length=60)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey(Product, unique=False)
    price = models.DecimalField(decimal_places=8, max_digits=16, default=0, verbose_name=u'Price', blank=True, null=True)

    shopping_place = models.ForeignKey(ShoppingPlace, blank=True, null=True)

    cart_item_assigned = models.ForeignKey('self', blank=True, null=True)

    class Meta:
        db_table = 'cart_items'
        ordering = ['date_added']

    def get_list_item_info(self, request=None):
        res = {
            'id': self.id,
            'prod_id': self.product.id,
            #deprecated
            'prod_name': self.product.name,
            #~deprecated
            'name': self.product.name,
            'sku': self.product.sku,
            'quantity': self.quantity
        }
        if self.shopping_place:
            res['place'] = self.shopping_place.name

        #todo
        res['options'] = {
            'priceable': [],
            'not_priceable': []
        }

        for opt in self.cartitemoption_set.all():
            list_item_info = opt.product_option.get_list_item_info()
            if ('priceable' in list_item_info):
                if (list_item_info['priceable']):
                    res['options']['priceable'].append(list_item_info)
                else:
                    res['options']['not_priceable'].append(list_item_info)
        #~todo

        res['thumbnail'] = self.product.get_thumbnail()

        toppings = CartItem.objects.filter(cart_item_assigned=self)
        if toppings.exists():
            res['toppings'] = []
            for topping in toppings:
                res['toppings'].append(topping.get_list_item_info(request))

        if request:
            if request.user.is_authenticated():
                from lugati.lugati_registration.models import LugatiUserProfile
                cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
                price_format_string = "%." + str(cur_company.default_currency.decimal_fields) +"f"
                res['btc_rate'] = cur_company.default_currency.btc_rate
                res['price'] = price_format_string % self.get_price()
                res['total'] = price_format_string % (self.get_price()*self.quantity)
                res['mbtc_price'] = price_format_string % (self.get_price()/cur_company.default_currency.btc_rate*1000)
                if not self.product.price_wo_discount:
                    res['price_wo_dicount'] = price_format_string % 0
                else:
                    res['price_wo_dicount'] = price_format_string % float(self.product.price_wo_discount)
                res['currency_icon_class'] = cur_company.default_currency.icon_class_name
            elif 'cur_path' in request.GET:
                resolved_path = resolve(request.GET['cur_path'])
                try:
                    pos_id = resolved_path.kwargs['pos_id']
                    place = ShoppingPlace.objects.get(pk=pos_id)
                    cur_company = place.shop.company
                    res['btc_rate'] = cur_company.default_currency.btc_rate
                    price_format_string = "%." + str(cur_company.default_currency.decimal_fields) +"f"
                    res['mbtc_price'] = price_format_string % (self.get_price()/cur_company.default_currency.btc_rate*1000)
                    res['currency_icon_class'] = cur_company.default_currency.icon_class_name
                except:
                    res['btc_rate'] = 1
                    price_format_string = "%.2f"
                    res['currency_icon_class'] = "fa fa-rub"
                    res['mbtc_price'] = '-'

                res['price'] = price_format_string % self.get_price()
                res['total'] = price_format_string % (self.get_price()*self.quantity)
                if self.product.price_wo_discount:
                    res['price_wo_dicount'] = price_format_string % self.product.price_wo_discount
                else:
                    res['price_wo_dicount'] = price_format_string % 0



        res['btc_rate'] = str(res['btc_rate'])
        return res

    def total(self):
        return self.quantity * self.get_price()

    def get_total_btc(self):
        if self.shopping_place:
            cur_company = self.shopping_place.shop.company
            if cur_company:
                return self.total()/cur_company.default_currency.btc_rate
        return 0

    def total_str(self):
        return str('%.2f' % (self.total(),))

    def name(self):
        return self.product.name

    def get_total_price(self):
        item_price = self.get_price()
        for topping in self.get_toppings():
            item_price += topping.get_price()
        return item_price

    def get_price(self):
        item_price = 0
        if (self.price):
            item_price = self.price
        else:
            item_price = self.product.get_price()
        return item_price

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        if self.quantity <= 0:
            self.delete()
        else:
            self.save()
        toppings = CartItem.objects.filter(cart_item_assigned=self)
        if toppings.exists():
            for topping in toppings:
                topping.quantity = self.quantity
                topping.save()

    def get_toppings(self):
        return CartItem.objects.filter(cart_item_assigned=self)

class CartDelivery(models.Model):
    cart_id = models.CharField(max_length=60)
    date_added = models.DateTimeField(auto_now_add=True)
    delivery_option = models.ForeignKey(DeliveryOption)
    cart_item = models.ForeignKey(CartItem, blank=True, null=True)

class CartItemOption(models.Model):
    cart_item = models.ForeignKey(CartItem)
    product_option = models.ForeignKey(ProductPropertyValue)
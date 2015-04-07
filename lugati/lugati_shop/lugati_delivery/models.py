
from django.db import models
from lugati.lugati_points_of_sale.models import City
from django.contrib.sites.models import Site
from lugati.products.models import Product



class DeliveryOption(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, blank=True, null=True)
    price = models.DecimalField(default=0, max_digits=15, decimal_places=8)
    additional_price = models.DecimalField(default=0, max_digits=15, decimal_places=8)
    site = models.ForeignKey(Site)
    online_payment = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    del_opt = models.IntegerField(default=1)

    mail_text = models.TextField(null=True, blank=True)
#todo!!!
    products = models.ManyToManyField(Product, null=True, blank=True)

    def get_list_item_info(self, request=None, export=False):

        res = {
            'id': self.id,
            'name': self.name,
            'price': "%.2f" % self.price,
            'additional_price': "%.2f" % self.additional_price,
            'online_payment': self.online_payment,
            'active': self.active,
            'del_opt': self.del_opt,
            'mail_text': self.mail_text
        }

        if self.city:
            res['city'] = self.city.get_list_item_info()

        return res

    def __unicode__(self):
        try:
            return self.name + " - " + self.city.name
        except:
            return 'none'

    class Meta:
        ordering = ['name']

class DeliveryPrice(models.Model):
    product = models.ForeignKey(Product)
    delivery_option = models.ForeignKey(DeliveryOption)
    price = models.DecimalField(default=0, max_digits=15, decimal_places=8)
    additional_price = models.DecimalField(default=0, max_digits=15, decimal_places=8)

    def __unicode__(self):
        try:
            return self.product.name + " - " + self.delivery_option.city.name + " - " + self.delivery_option.name
        except:
            return 'none'
    class Meta:
        ordering = ['product','delivery_option']
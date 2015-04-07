from django.db import models
# from lugati.lugati_shop.models import Shop
from gcm.models import AbstractDevice
# from lugati.lugati_shop.models import ShoppingPlace

class LugatiDevice(AbstractDevice):
    # shop = models.ForeignKey(Shop, null=True, blank=True)
    # shopping_place = models.ForeignKey(ShoppingPlace, null=True, blank=True)
    #is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name
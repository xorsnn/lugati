# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.sites.models import Site
from lugati.lugati_shop.models import Shop
from lugati.products.models import Product
from django.conf import settings

class City(models.Model):
    parent_object = models.ForeignKey('self', blank=True, null=True, verbose_name=u'Category')
    is_category = models.BooleanField(default=False)
    # region = models.ForeignKey('self', blank=True, null=True, verbose_name=u'Регион')
    # is_region = models.BooleanField(default=False)
    site = models.ForeignKey(Site)
    name = models.CharField(max_length=400)
    priority = models.IntegerField(default=1)
    comment = models.TextField(blank=True, null=True)

    lng = models.CharField(max_length=100, verbose_name=u'Долгота', null=True, blank=True)
    lat = models.CharField(max_length=100, verbose_name=u'Широта', null=True, blank=True)

    class Meta:
        ordering = ['-priority', 'name']

    def __unicode__(self):
        return self.name

    def get_list_item_info(self, request=None, export=False):

        res = {
            'id': self.id,
            'is_category': self.is_category,
            'name': self.name,
            'priority': self.priority,
            'comment': 'base_id='+str(self.id),
            'lng': str(self.lng),
            'lat': str(self.lat)
        }

        if self.parent_object:
            res['parent_object'] = self.parent_object.get_list_item_info()

        return res


class SalesPoint(models.Model):

    site    = models.ForeignKey(Site)
    name    = models.CharField(max_length=400)
    address = models.TextField()
    description = models.TextField()
    link    = models.CharField(max_length=400)

    product = models.ForeignKey(Product, null=True, blank=True)
    city    = models.ForeignKey(City, null=True, blank=True)
    shop    = models.ForeignKey(Shop, null=True, blank=True)

    lng     = models.CharField(max_length=100, null=True, blank=True)
    lat     = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_cur_server(self):
        if settings.POS_SERVER:
            return settings.POS_SERVER
        else:
            return ''
# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models
from PIL import Image
from lugati.lugati_media.models import ThebloqImage
from django.contrib.sites.models import Site
from lugati.lugati_shop.models import LugatiCompany
from django.conf import settings
from django.core.urlresolvers import resolve
from lugati.lugati_shop.models import ShoppingPlace
import logging

logger = logging.getLogger(__name__)


class Brand(models.Model):
    name = models.CharField(max_length=400)
    description = models.TextField()
    site = models.ForeignKey(Site)

    def __unicode__(self):
        return self.name


class AbstractProduct(models.Model):
    dt_modify = models.DateTimeField(auto_now=True)
    dt_add = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class Product(AbstractProduct):
    parent_object = models.ForeignKey('self', blank=True, null=True, verbose_name=u'Category')

    code = models.CharField(max_length=100, blank=True, verbose_name=u'Code')
    sku = models.CharField(max_length=50, blank=True, verbose_name=u'Sku')

    name = models.CharField(max_length=200, verbose_name=u'Name')
    description = models.TextField(blank=True, verbose_name=u'Description')

    # mps
    styled_name = models.TextField(blank=True, verbose_name=u'Styled name')
    styled_description = models.TextField(blank=True, verbose_name=u'Styled description')
    # ~mps

    preview = models.TextField(blank=True, verbose_name=u'Preview')
    is_category = models.BooleanField(default=False)

    # topping
    is_topping = models.BooleanField(default=False)
    assigned_to = models.ManyToManyField('self', blank=True, null=True, related_name='assigned_to')
    # ~topping

    active = models.BooleanField(default=True, verbose_name=u'Active')
    priority = models.IntegerField(default=1, verbose_name=u'Order', blank=True, null=True)

    thumbnail = models.ForeignKey(ThebloqImage, blank=True, null=True)

    site = models.ForeignKey(Site)
    company = models.ForeignKey(LugatiCompany, blank=True, null=True)

    brand = models.ForeignKey(Brand, blank=True, null=True, verbose_name=u'Производитель')
    additional_info = models.TextField(blank=True, verbose_name=u'Дополнительная информация')
    in_stock = models.BooleanField(default=True)

    price_wo_discount = models.FloatField(default=0, verbose_name=u'Цена без скидки', blank=True, null=True)
    price = models.DecimalField(decimal_places=8, max_digits=16, default=0, verbose_name=u'Price', blank=True,
                                null=True)

    # SEO
    # seo_title       = models.TextField(verbose_name=u'SEO title')
    # seo_description = models.TextField(verbose_name=u'SEO description')
    # seo_keywords    = models.TextField(verbose_name=u'SEO keywords')
    #~SEO

    def __unicode__(self):
        if self.is_topping:
            if self.parent_object:
                return self.name + ' (' + self.parent_object.name + ')'

        return self.name

    class Meta:
        ordering = ['-is_category', '-priority', 'name', 'styled_name']

    def save(self, *args, **kwargs):
        if not self.priority:
            if settings.SHOP_TYPE == 'MPS':
                if self.company:
                    from django.db.models import Max

                    res = Product.objects.filter(company=self.company).aggregate(Max('priority'))
                    logger.info('res: ' + str(res))
                    if res['priority__max']:
                        self.priority = res['priority__max'] + 1
                    else:
                        self.priority = 1
        super(Product, self).save(*args, **kwargs)


    def get_list_item_info(self, request=None, hierarchy=False):

        node = {
            'id': self.id,
            'content_type_id': ContentType.objects.get_for_model(Product).id,
            'name': self.name,
            'name_preview': str(self),
            'styled_name': self.styled_name,
            'styled_description': self.styled_description,
            'is_category': self.is_category,
            'priority': self.priority,
            'preview': self.preview,
            'editing_mode': False,
            'in_stock': self.in_stock,
            'images': []
        }

        if settings.SHOP_TYPE == 'MPS':
            node['styled_name_to_edit'] = self.styled_name
            node['styled_description_to_edit'] = self.styled_description

        if self.parent_object:
            node['parent_id'] = self.parent_object.id
        if self.is_category:
            children = Product.objects.filter(parent_object=self).filter(is_topping=False)
            node['number_of_items'] = children.count()
            node['children_type'] = 'items'
            if children.count() > 0:
                if children[0].is_category:
                    node['children_type'] = 'subcategories'

        if self.parent_object:
            node['parent_id'] = self.parent_object.id

        if hierarchy:
            def get_parent(obj):
                if obj.parent_object:

                    new_node = {
                        'name': obj.parent_object.name,
                        'id': obj.parent_object.id,
                        'content_type_id': ContentType.objects.get_for_model(Product).id
                    }

                    return get_parent(obj.parent_object) + [new_node]
                else:
                    return []

            node['hierarchy'] = get_parent(self)

        if (settings.SHOP_TYPE == 'MPS') and self.company:
            node['mbtc_rate'] = float(self.company.default_currency.btc_rate)

        # product options
        if (settings.SHOP_TYPE == 'MPS') and (not self.is_category):

            node['variations'] = {}
            try:
                prop_priceable = ProductProperty.objects.get(product=self, name='mps_priceable')
            except:
                prop_priceable = None
            if prop_priceable:
                prop_values = ProductPropertyValue.objects.filter(product_property=prop_priceable)
                node['variations']['priceable'] = []
                for prop_value in prop_values:
                    if prop_value.name.replace('<br>', '').strip() == '':
                        prop_value.delete()
                    else:
                        node['variations']['priceable'].append(prop_value.get_list_item_info(request))

            try:
                prop_not_priceable = ProductProperty.objects.get(product=self, name='mps_not_priceable')
            except:
                prop_not_priceable = None
            if prop_not_priceable:
                prop_values = ProductPropertyValue.objects.filter(product_property=prop_not_priceable)
                node['variations']['not_priceable'] = []
                for prop_value in prop_values:
                    if prop_value.name.replace('<br>', '').strip() == '':
                        prop_value.delete()
                    else:
                        node['variations']['not_priceable'].append(prop_value.get_list_item_info(request))

                    # ~product options

        if request:
            if 'cur_path' in request.GET:
                resolved_path = resolve(request.GET['cur_path'])
                try:
                    pos_id = resolved_path.kwargs['pos_id']
                    place = ShoppingPlace.objects.get(pk=pos_id)
                    cur_company = place.shop.company
                    price_format_string = "%." + str(cur_company.default_currency.decimal_fields) + "f"
                    node['price'] = price_format_string % self.get_price()
                    node['price_wo_dicount'] = price_format_string % self.get_price_wo_discount()
                    node['currency_icon_class'] = cur_company.default_currency.icon_class_name
                except:
                    if request.user.is_authenticated():
                        from lugati.lugati_registration.models import LugatiUserProfile

                        node['currency_icon_class'] = LugatiUserProfile.objects.get(
                            user=request.user).get_company().default_currency.icon_class_name
                        node['editing_mode'] = True
                    node['price'] = "%.2f" % self.get_price()
                    node['price_wo_dicount'] = "%.2f" % self.get_price_wo_discount()
            else:
                if request.user.is_authenticated():
                    node['editing_mode'] = True
                    from lugati.lugati_registration.models import LugatiUserProfile

                    node['currency_icon_class'] = LugatiUserProfile.objects.get(
                        user=request.user).get_company().default_currency.icon_class_name
                node['price'] = "%.2f" % self.get_price()
                node['price_wo_dicount'] = "%.2f" % self.get_price_wo_discount()

        else:
            node['price'] = "%.2f" % self.get_price()
            node['price_wo_dicount'] = "%.2f" % self.get_price_wo_discount()

        if request:
            if 'thumbnail_size_str' in request.GET:
                thumbnail_size_str = request.GET['thumbnail_size_str']
            else:
                thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE

            if settings.SHOP_TYPE == 'MPS':
                thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE
        else:
            thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE

        node['has_thumbnail'] = True
        node['thumbnail'] = self.get_thumbnail(thumbnail_size_str)
        node['default_thumbnail'] = self.get_default_thumbnail(thumbnail_size_str)

        if not node['thumbnail']:
            node['has_thumbnail'] = False
            del node['thumbnail']

        for img in self.get_images():
            img_node = img.get_list_item_info()
            node['images'].append(img_node)

        # toppings
        if self.is_topping:
            if 'assigned_to_id' in request.GET:
                try:
                    if (self.assigned_to.all().filter(pk=request.GET['assigned_to_id']).exists()):
                        node['active_topping'] = True
                except Exception, e:
                    pass
        else:
            if self.assigned_to.filter(in_stock=True).count() > 0:
                node['has_toppings'] = True
        # ~toppings

        return node

    def get_thumbnail(self, thumbnail_size_str="110x110"):
        img_node = None
        if self.thumbnail:
            img_node = self.thumbnail.get_list_item_info()
        else:
            for img in self.get_images():
                # todo!!!
                self.thumbnail = img
                self.save()
                img_node = img.get_list_item_info()
                break
        return img_node

    def get_default_thumbnail(self, thumbnail_size_str="110x110"):
        img = self.get_default_image()
        img_node = img.get_list_item_info()
        return img_node

    def get_default_image(self):
        default_name = 'default_product_image'
        try:
            img = ThebloqImage.objects.get(name=default_name)
        except:
            import os
            from django.core.files import File

            img = ThebloqImage()
            img.file = File(open(os.path.join(settings.STATIC_ROOT + '/lugati_admin/img/mps/', 'monochrome_logo.png')))
            img.name = default_name
            img.save()
        return img

    def is_hierarchical(self):
        return True

    def get_price_str(self):
        return str('%.2f' % (self.get_price(),))

    def get_images(self):
        return ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(Product))


    def get_main_image(self):
        if self.thumbnail:
            return self.thumbnail
        else:
            imgs = ThebloqImage.objects.filter(object_id=self.id,
                                               content_type=ContentType.objects.get_for_model(Product))
            if imgs.count() > 0:
                return imgs[0]
            else:
                default_imgs = ThebloqImage.objects.filter(slug="DEFAULT_IMAGE")
                if default_imgs.exists():
                    return default_imgs[0]
                else:
                    return self.get_default_image()

    def get_top_category(self):
        if self.is_category:
            logger.info("4 " + self.name)
            if self.parent_object:
                return self.parent_object.get_top_category()
            else:
                return self
        else:
            logger.info("2 " + self.name)
            if self.parent_object:
                return self.parent_object.get_top_category()
            else:
                return None

    def getDescription(self):
        return self.description.replace('\n', '<br>')


    def getChildren(self):
        return Product.objects.filter(parent_object=self)


    def get_prices(self):
        return ProductPrice.objects.filter(product=self)

    def get_price(self, product_property_value=None):
        if product_property_value:
            try:
                prod_price = ProductPrice.objects.get(product=self, product_property_value=product_property_value)
                return prod_price.price
            except:
                return 0
        else:
            if self.price:
                return self.price
            else:
                return 0

                # deprecated

    def setPrice(self, new_price):
        if new_price:
            pr_price = ProductPrice()
            pr_price.product = self
            pr_price.price = new_price
            pr_price.save()
            #~deprecated

    def set_price(self, new_price):
        if new_price:
            pr_price = ProductPrice()
            pr_price.product = self
            pr_price.price = new_price
            pr_price.save()

    def get_price_wo_discount(self):
        if self.price_wo_discount:
            return self.price_wo_discount
        else:
            return 0


class ProductProperty(models.Model):
    product = models.ForeignKey(Product)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class ProductPropertyValue(models.Model):
    product_property = models.ForeignKey(ProductProperty)
    default = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']

    def get_list_item_info(self, request=None, hierarchy=False):

        node = {
            'id': self.id,
            'content_type_id': ContentType.objects.get_for_model(ProductPropertyValue).id,
            'property_name': self.product_property.name,
            'property_id': self.product_property.id,
            'default': self.default,
            'active': self.default,
            'name': self.name,
            'value': self.value
        }

        if self.product_property.name == 'mps_priceable':
            node['priceable'] = True
            node['price'] = "%.2f" % self.product_property.product.get_price(self)
        else:
            node['priceable'] = False

        return node


class ProductPrice(models.Model):
    product = models.ForeignKey(Product)
    product_property_value = models.ForeignKey(ProductPropertyValue, null=True, blank=True)
    price = models.DecimalField(default=0, decimal_places=8, max_digits=20)
    price_d = models.DecimalField(default=0, decimal_places=8, max_digits=20)

    dt_modify = models.DateTimeField(auto_now=True)
    dt_add = models.DateTimeField(auto_now_add=True, editable=False)


class Bestseller(models.Model):
    product = models.ForeignKey(Product, primary_key=True)


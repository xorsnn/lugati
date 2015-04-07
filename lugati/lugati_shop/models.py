from django.db import models
from lugati.lugati_media.models import ThebloqImage
from lugati.lugati_media.models import ThebloqFont
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
from django.contrib.sites.models import Site
import logging
from lugati.lugati_mobile.models import LugatiDevice
from django.contrib.auth.models import User
from django.core.files import File

import StringIO
logger = logging.getLogger(__name__)


class FontSetting(models.Model):
    path = models.CharField(max_length=400)

class PhoneNumber(models.Model):
    number = models.CharField(max_length=50)
    site = models.ForeignKey(Site)

class LugatiCurrency(models.Model):
    name = models.CharField(max_length=50)
    decimal_fields = models.IntegerField(default=2)
    icon_class_name = models.CharField(max_length=100)
    btc_rate = models.DecimalField(max_digits=15, decimal_places=8, blank=True, null=True)
    stripe_str = models.CharField(max_length=3)

    def __unicode__(self):
        return self.name

class LugatiCompany(models.Model):

    name = models.CharField(max_length=100)
    default_currency = models.ForeignKey(LugatiCurrency)

    description = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=100, blank=True, null=True)

    twitter_link = models.CharField(max_length=400, blank=True, null=True)
    facebook_link = models.CharField(max_length=400, blank=True, null=True)
    website_link = models.CharField(max_length=400, blank=True, null=True)

    company_logo = models.ForeignKey(ThebloqImage, null=True, blank=True)

    #qr code for payment screen
    top_title = models.TextField(blank=True, null=True)
    bottom_title = models.TextField(blank=True, null=True, default="Scan or tap to pay")
    #~

    # payment
    stripe_secret_key = models.CharField(max_length=100, blank=True, null=True)
    stripe_public_key = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_qr_code(self):
        codes = ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(self)).filter(name='test_qr_code')
        if codes.count() == 0:

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=1,
            )

            qr.add_data('http://merchant.mycelium.com/')
            qr.make(fit=True)
            img = qr.make_image()
            (w, h) = img.size

            new_im = Image.new("RGB", (w, h), '#ffffff')

            new_im.paste(img, (0, 0))

            d = ImageDraw.Draw(new_im)

            import StringIO

            tempfile_io = StringIO.StringIO()
            new_im.save(tempfile_io, format='PNG')

            tb_image = ThebloqImage()
            from django.core.files.uploadedfile import InMemoryUploadedFile

            tb_image.file = InMemoryUploadedFile(tempfile_io, None, 'qr-code.jpg', 'image/png', tempfile_io.len, None)
            # tb_image.content_object = self
            tb_image.name = 'test_qr_code'
            tb_image.save()
        else:
            tb_image = codes[0]

        return tb_image

    def get_logo_attributes(self):
        if self.get_images().count() > 0:
            return {
                'menu_padding': '160px',
                'logo_padding': '5px 0'
            }
        else:
            return {
                'menu_padding': '70px',
                'logo_padding': '15px 0'
            }

    def get_logo_url(self, request = None):
        aspect_ratio = 1
        if self.get_images().count() > 0:
            img = self.get_images()[0]
            return img.get_thumbnail('150x150', get_native_image=True).url
        else:
            if request:
                if settings.SITE_ID == 6:
                    return '/media/custom/mps/img/small_logo.png'
                else:
                    return '/media/custom/lugati_site/img/logo_small.png'
            else:
                return '/media/custom/mps/img/small_logo.png'

    def get_images(self):
        return ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(LugatiCompany))

    def get_content_type_id(self):
        return ContentType.objects.get_for_model(LugatiCompany).id

    def get_list_item_info(self, request=None):
        node = {
            'id': self.id,
            'content_type_id': self.get_content_type_id(),
            'name': self.name,
            # 'images': []
        }

        logo_size_str = "220x220"

        node['has_logo'] = True
        node['logo'] = self.get_logo(logo_size_str)
        # node['default_logo'] = self.get_default_logo(logo_size_str)

        if not node['logo']:
            node['has_logo'] = False
            del node['logo']

        return node

    def get_logo(self, thumbnail_size_str="220x220"):
        img_node = None
        if self.company_logo:
            img_node = self.company_logo.get_list_item_info()
        return img_node

    def get_default_logo(self, thumbnail_size_str="220x40"):
        img = self.get_default_image()
        img_node = img.get_list_item_info()
        return img_node


class LugatiShoppingSession(models.Model):
    cart_id = models.CharField(max_length=60)
    company = models.ForeignKey(LugatiCompany)
    is_admin = models.BooleanField(default=False)

class Shop(models.Model):
    name = models.CharField(max_length=50)
    company = models.ForeignKey(LugatiCompany, null=True, blank=True)
    background_color = models.CharField(max_length=10, default='none')
    text_color = models.CharField(max_length=10, default='#555')
    text_font = models.ForeignKey(ThebloqFont, blank=True, null=True)
    font_size = models.IntegerField(default=14)

    def __unicode__(self):
        return self.name

    def get_setting(self):
        return self.active_setting

    def get_logo(self):
        imgs = ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(Shop))
        if imgs.count() > 0:
            return imgs[0]
        else:
            file_name = os.path.join(settings.STATIC_ROOT, 'custom/mps/img/lugati_default/default_logo.png')
            tb_image = ThebloqImage()
            tb_image.file = File(open(file_name))
            tb_image.content_object = self
            tb_image.save()
            return tb_image

class ShoppingPlace(models.Model):

    shop = models.ForeignKey(Shop)
    name = models.CharField(max_length=50)
    top_title = models.TextField(null=True, blank=True)
    bottom_title = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_list_item_info(self, request=None):

        node = {
            'id': self.id,
            'content_type_id': ContentType.objects.get_for_model(ShoppingPlace).id,
            'name': self.name,
            'editing_mode': False,
            'top_title': self.top_title,
            'bottom_title': self.bottom_title,
            'qr_code_url': self.get_cur_server() + self.get_qr_code().file.url
        }
        return node

    def get_cur_server(self):
        if settings.POS_SERVER:
            return settings.POS_SERVER
        else:
            return ''

    def get_qr_code(self):
        codes = ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(self))
        codes.delete()
        if False:
            pass
        else:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=1,
            )

            qr.add_data(self.get_cur_server() + '/catalog/point_of_sale/start/' + str(self.id))
            qr.make(fit=True)
            img = qr.make_image()
            (w, h) = img.size
            new_im = Image.new("RGB", (w, h), '#ffffff')
            new_im.paste(img, (0, 0))
            d = ImageDraw.Draw(new_im)

            tempfile_io = StringIO.StringIO()
            new_im.save(tempfile_io, format='PNG')

            tb_image = ThebloqImage()
            from django.core.files.uploadedfile import InMemoryUploadedFile

            tb_image.file = InMemoryUploadedFile(tempfile_io, None, 'qr-code.jpg', 'image/png', tempfile_io.len, None)
            tb_image.content_object = self
            tb_image.save()
            return tb_image

class LugatiClerk(models.Model):
    name = models.CharField(max_length=100)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    company = models.ForeignKey(LugatiCompany, null=True, blank=True)
    models.ManyToManyField(ShoppingPlace)
    device = models.ForeignKey(LugatiDevice, null=True, blank=True)
    reg_id = models.CharField(max_length=500, null=True, blank=True)
    active = models.BooleanField(default=True)
    branch = models.ForeignKey(Shop, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    raiting = models.IntegerField(default=5)
    # user = models.ForeignKey(User, primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return self.login

    def lugati_delete(self):
        self.user.delete()
        self.delete()

    def get_images(self):
        return ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(LugatiClerk))

    def get_list_item_info(self, request=None):

        node = {
            'id': self.id,
            'content_type_id': ContentType.objects.get_for_model(LugatiClerk).id,
            'name': self.name,
            'editing_mode': False,
            'images': []
        }
        thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE
        has_images = False
        for img in self.get_images():
            img_node = img.get_list_item_info()
            img_node['base_url'] = img.file.url
            img_node['image_url'], img_node['image_margin'] = img.get_thumbnail_attributes(img.get_thumbnail(thumbnail_size_str, get_native_image=True), thumbnail_size_str)
            node['images'].append(img_node)
            has_images = True
        return node

    def get_main_image(self):
        imgs = self.get_images()
        if imgs.count() > 0:
            return imgs[0]
        else:
            return self.get_default_image()

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

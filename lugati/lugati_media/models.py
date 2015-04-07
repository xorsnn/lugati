# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.conf import settings

from sorl.thumbnail.images import ImageFile, DummyImageFile
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry
from sorl.thumbnail import get_thumbnail
from django.conf import settings
import logging
from django.contrib.sites.models import Site

import base64

logger = logging.getLogger(__name__)

class ThebloqVideo(models.Model):
    site = models.ForeignKey(Site)
    name = models.CharField(max_length=400)
    video_id = models.CharField(max_length=100)
    vimeo_id = models.CharField(max_length=100)
    video_code = models.TextField()

    def __unicode__(self):
        return self.name

class ThebloqFont(models.Model):
    file = models.FileField(upload_to="thebloq_fonts")

    slug = models.SlugField(max_length=400, blank=True)

    def __unicode__(self):
        return self.file.name

    def get_url(self):
        return settings.MEDIA_URL + self.file.name

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(ThebloqFont, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(ThebloqFont, self).delete(*args, **kwargs)

class ThebloqImage(models.Model):
    file = models.ImageField(upload_to="thebloq_pics")
    slug = models.SlugField(max_length=400, blank=True)
    name = models.CharField(max_length=400, blank=True)

    content_type    = models.ForeignKey(ContentType, null=True, blank=True)
    object_id       = models.PositiveIntegerField(null=True, blank=True)
    content_object  = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.file.name

    def get_url(self):
        return settings.MEDIA_URL + self.file.name

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(ThebloqImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(ThebloqImage, self).delete(*args, **kwargs)

    def to_string(self):
        encoded_string = base64.b64encode(self.file.read())
        return encoded_string

    def get_list_item_info(self, request=None):
        thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE
        node = {
            'id': self.id,
            'name': str(self),
            'url': self.file.url,
            'width': self.file.width,
            'height': self.file.height
        }
        node['base_url'] = self.file.url
        node['image_url'], node['image_margin'] = self.get_thumbnail_attributes(self.get_thumbnail(thumbnail_size_str, get_native_image=True), thumbnail_size_str)
        node['http_path'] = node['base_url']
        return node

    def get_thumbnail_attributes(self, image_thm, size_str):
        if image_thm:
            margin = [0, 0, 0, 0]
            image_file = default.kvstore.get_or_set(ImageFile(image_thm))
            x, y = parse_geometry(size_str, image_file.ratio)
            ex = x - image_file.x
            margin[3] = ex / 2
            margin[1] = ex / 2
            if ex % 2:
                margin[1] += 1
            ey = y - image_file.y
            margin[0] = ey / 2
            margin[2] = ey / 2
            if ey % 2:
                margin[2] += 1
            margin_str = ' '.join(['%spx' % n for n in margin])


            res_dt = {
                'margin_str': margin_str,
            }
            if settings.LUGATI_FULL_IMAGE_PATH:
                res_dt['thumbnail_url'] = settings.POS_SERVER + image_thm.url
            else:
                res_dt['thumbnail_url'] = image_thm.url
        else:
            res_dt = {
                'thumbnail_url': '',
                'margin_str': ''
            }
        return res_dt['thumbnail_url'], res_dt['margin_str']

    def get_thumbnail(self, size_str, crop=None, get_native_image=False):
        try:
            if get_native_image:
                image_thm = get_thumbnail(self.file, size_str, quality=100, padding=True, colorspace='RGB', padding_color='#ffffff')
            elif crop:
                image_thm = get_thumbnail(self.file, size_str, quality=100, crop=crop)
            else:
                image_thm = get_thumbnail(self.file, size_str, quality=100)
            return image_thm
        except Exception, e:
            logger.info('thumbnail_error: ' + str(e))
            return None



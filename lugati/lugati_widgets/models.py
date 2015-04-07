from django.db import models
from lugati.lugati_media.models import ThebloqImage
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.sites.models import Site

class LugatiBaseTextBlock(models.Model):
    text = models.TextField(blank=True)
    site = models.ForeignKey(Site)
    dt_modify = models.DateTimeField(auto_now=True)
    dt_add = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True

class LugatiTextBlock(LugatiBaseTextBlock):
    name = models.CharField(max_length=400)

    def __unicode__(self):
        return str(self.id) + " | " + self.name

    def get_list_item_info(self, request=None, export=False):
        return {
            'id': self.id,
            'name': str(self),
            'text': self.text
        }

class LugatiNews(LugatiBaseTextBlock):
    name = models.CharField(max_length=400)

    def __unicode__(self):
        return str(self.id) + " | " + str(self.dt_add) + " | " + self.name

    def get_list_item_info(self, request=None, export=False):
        return {
            'id': self.id,
            'name': str(self),
            'text': self.text
        }

class LugatiPoem(LugatiBaseTextBlock):
    name = models.CharField(max_length=400)

    def __unicode__(self):
        return str(self.id) + " | " + str(self.dt_add) + " | " + self.name

    def get_list_item_info(self, request=None, export=False):
        node = {
            'id': self.id,
            'name': str(self),
            'text': self.text,
            'images': []
        }

        if request:
            if 'thumbnail_size_str' in request.GET:
                thumbnail_size_str = request.GET['thumbnail_size_str']
            else:
                thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE
        else:
            thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE

        for img in self.get_images():
            if export:
                img_node = img.to_string()
            else:
                img_node = {'id': img.id}
                img_node['image_url'], img_node['image_margin'] = img.get_thumbnail_attributes(img.get_thumbnail(thumbnail_size_str, get_native_image=True),thumbnail_size_str)
            node['images'].append(img_node)
        return node

    def get_images(self):
        return ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(LugatiPoem))


class LugatiPortfolioItem(LugatiBaseTextBlock):
    name = models.CharField(max_length=400)

    def __unicode__(self):
        return str(self.id) + " | " + str(self.dt_add) + " | " + self.name

    def get_list_item_info(self, request=None):
        node = {
            'id': self.id,
            'name': str(self),
            'text': self.text,
            'images': []

        }
        if request:
            if 'thumbnail_size_str' in request.GET:
                thumbnail_size_str = request.GET['thumbnail_size_str']
            else:
                thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE
        else:
            thumbnail_size_str = settings.DEFAULT_THUMBNAIL_SIZE

        for img in self.get_images():
            img_node = {'id':img.id}
            img_node['image_url'], img_node['image_margin'] = img.get_thumbnail_attributes(img.get_thumbnail(thumbnail_size_str, get_native_image=True), thumbnail_size_str)
            node['images'].append(img_node)
        return node

    def get_images(self):
        return ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(LugatiPortfolioItem))

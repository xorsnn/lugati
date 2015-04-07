from django.db import models
from lugati.lugati_media.models import ThebloqImage
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.conf import settings

class GalleryItem(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    site = models.ForeignKey(Site)

    def get_images(self):
        return ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(GalleryItem))

    def get_list_item_info(self, request=None):
        node = {
            'id': self.id,
            'name': self.title,
            'has_images': True,
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
            img_node = img.get_list_item_info()
                # 'id': img.id
            # }
            # img_node['image_url'], img_node['image_margin'] = img.get_thumbnail_attributes(img.get_thumbnail(thumbnail_size_str, get_native_image=True),thumbnail_size_str)
            node['images'].append(img_node)
        return node


class LugatiSlider(models.Model):
    site = models.ForeignKey(Site)

class SliderItem(models.Model):
    slider = models.ForeignKey(LugatiSlider, null=True, blank=True)
    link = models.CharField(max_length=400)
    def get_images(self):
        return ThebloqImage.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(SliderItem))
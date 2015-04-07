from django.shortcuts import render
from lugati.lugati_media.lugati_gallery.models import GalleryItem
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.http import HttpResponse
from django.contrib.sites.models import Site
from django.contrib.sites.models import get_current_site
from lugati.lugati_media.models import ThebloqImage
import logging
logger = logging.getLogger(__name__)
from lugati.lugati_media.models import ThebloqVideo
import json

class CreateGalleryItem(CreateView):
    model = GalleryItem

    def form_valid(self, form):
        self.object = form.save()

        return HttpResponse()

class UpdateGalleryItem(UpdateView):
    model = GalleryItem

    def form_valid(self, form):
        self.object = form.save()

        return HttpResponse()

class DeleteGalleryItem(DeleteView):
    model = GalleryItem


def get_galleries(request):
    cur_site = get_current_site(request)
    def get_galleries_tree(gallery_group=None, level=0):
        dt = []
        galleries = GalleryItem.objects.filter(site=cur_site).order_by('id')
        for gallery in galleries:
            cur_node = {
                'label': gallery.title,
                'uid': gallery.id,
                'data': {
                    'definition': gallery.title
                }
            }

            dt.append(cur_node)
        return dt

    res_dt = get_galleries_tree()
    return HttpResponse(json.dumps(res_dt))

def get_update_gallery_template(request, gallery_id = ''):
    return render(request, 'lugati_admin/lugati_media/lugati_gallery/list_gallery_items.html')

def get_gallery_images(request, gallery_id = ''):
    res_dt = {
        'images' : []
    }
    images = GalleryItem.objects.get(pk=gallery_id).get_images()

    return HttpResponse(json.dumps(res_dt))

def update_gallery_images(request, gallery_id = ''):
    res_dt = {}
    gallery = GalleryItem.objects.get(pk=gallery_id)
    pic_array = request.GET['pic_array']
    pic_id_array = pic_array.split(';')
    for pic_id in pic_id_array:
        if pic_id <> '':
            try:
                tb_image = ThebloqImage.objects.get(id=pic_id)
                tb_image.content_object = gallery
                tb_image.save()
            except:
                logger.info('image with id ' + str(pic_id) + " doesn't exists")

    return HttpResponse(json.dumps(res_dt))

def get_images(request):
    res_dt = {}
    res_dt['images'] = []
    galleries = GalleryItem.objects.all()
    for gallery in galleries:
        for img in gallery.get_images():
            img_url, size_str = img.get_thumbnail_attributes(img.get_thumbnail('168x168', crop='center'),'168x168')
            new_img = {
                'img_url': img_url,
                'original_url': img.file.url,
                'size_str': size_str
            }
            res_dt['images'].append(new_img)
    return HttpResponse(json.dumps(res_dt))

def get_videos(request):
    cur_site = get_current_site(request)
    def get_videos_tree(gallery_group=None, level=0):
        dt = []
        videos = ThebloqVideo.objects.filter(site=cur_site).order_by('id')
        for video in videos:
            cur_node = {
                'label': video.name,
                'uid': video.id,
                'data': {
                    'definition': video.name
                }
            }
            dt.append(cur_node)
        return dt

    res_dt = get_videos_tree()
    return HttpResponse(json.dumps(res_dt))

# encoding: utf-8
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, DetailView
from django.views.generic import CreateView, DeleteView, ListView
from django.shortcuts import render
from django.http import HttpResponse
import json
from django.contrib.sites.models import get_current_site
from django.views.decorators.csrf import csrf_exempt
from .models import ThebloqImage
from .serialize import serialize
from .response import JSONResponse, response_mimetype
from sorl.thumbnail import get_thumbnail
from django.contrib.contenttypes.models import ContentType
from lugati.lugati_media.lugati_gallery.models import GalleryItem

import logging
from lugati.products.models import Product
from lugati.lugati_shop.models import Shop#, ShopSetting
from lugati.lugati_media.models import ThebloqVideo
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from lugati import lugati_procs
from PIL import Image
from django.core.files import File

logger = logging.getLogger(__name__)

PREVIEW_SIZE = 220, 220


@csrf_exempt
def mps_get_image(request, image_id):
    res_dt = {}
    pic = ThebloqImage.objects.get(pk=image_id)
    res_dt = pic.get_list_item_info()
    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def mps_assign_thumbnail(request, content_object_id, object_id, image_id):
    res_dt = {}
    pic = ThebloqImage.objects.get(pk=image_id)

    if settings.SHOP_TYPE == 'MPS':
        if pic.file.height <> pic.file.width:
            if pic.file.height > pic.file.width:
                size_str = str(pic.file.width) + 'x' + str(pic.file.width)
            else:
                size_str = str(pic.file.height) + 'x' + str(pic.file.height)
            thum = pic.get_thumbnail(size_str, crop='center')
            pic.file = File(open(thum.storage.location + '/' + thum.name))
            pic.save()

    model_class = ContentType.objects.get(pk=content_object_id).model_class()
    object = model_class.objects.get(pk=object_id)

    if model_class.__name__ == 'Product':
        object.thumbnail = pic
    elif model_class.__name__ == 'LugatiCompany':
        object.company_logo = pic
    else:
        pic.content_object = object
        pic.save()
    object.save()

    # if model_class.__name__ == 'LugatiCompany':
    #     object.get_images().delete()
    #
    # pic.content_object = object
    # pic.save()

    res_dt = pic.get_list_item_info(request)
    res_dt['content_object_class_name'] = model_class.__name__

    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def mps_assign_image(request, content_object_id, object_id, image_id):
    res_dt = {}
    pic = ThebloqImage.objects.get(pk=image_id)

    model_class = ContentType.objects.get(pk=content_object_id).model_class()
    object = model_class.objects.get(pk=object_id)

    if model_class.__name__ == 'LugatiCompany':
        object.get_images().delete()

    pic.content_object = object
    pic.save()

    res_dt = pic.get_list_item_info(request)

    return HttpResponse(json.dumps(res_dt))


def get_aspect_ratio(request, content_object_id = ''):
    model_class = ContentType.objects.get(pk=content_object_id).model_class()
    if model_class.__name__ == 'LugatiCompany':
        # return HttpResponse(json.dumps({'aspect_ratio': 5.5}))
        return HttpResponse(json.dumps({'aspect_ratio': 1}))
    else:
         return HttpResponse(json.dumps({'aspect_ratio': 1}))


@csrf_exempt
def mps_crop_image(request, content_object_id = '', image_id=''):

    model_class = ContentType.objects.get(pk=content_object_id).model_class()

    if model_class.__name__ != 'LugatiCompany':
        PREVIEW_SIZE = 400, 400
    else:
        PREVIEW_SIZE = 220, 220

    params = json.loads(request.body)
    pic = ThebloqImage.objects.get(pk=image_id)

    height  = int(round(float(params['coords']['h'])))
    width   = int(round(float(params['coords']['w'])))
    x       = int(round(float(params['coords']['x'])))
    y       = int(round(float(params['coords']['y'])))

    im = Image.open(pic.file.file.name)
    if im.mode != "RGB":
        im = im.convert("RGB")

    im.crop((x, y, x+width, y+height)).save(pic.file.file.name)

    im = Image.open(pic.file.file.name)
    im = im.resize(PREVIEW_SIZE, Image.ANTIALIAS)
    im.save(pic.file.file.name)
    pic.file = File(open(pic.file.file.name))
    pic.save()

    res_dt = pic.get_list_item_info()
    # res_dt = {
    #     'image_url': pic.file.url,
    #     'pic_id': pic.id,
    #     'width': PREVIEW_SIZE[0],
    #     'height': PREVIEW_SIZE[1]
    # }

    return HttpResponse(json.dumps(res_dt))

@csrf_exempt
def remove_image(request, image_id=''):

    image = ThebloqImage.objects.get(pk=image_id)
    image.content_object = None
    image.save()
    return HttpResponse(json.dumps({}))

@csrf_exempt
def upload_image_new(request):
    from django import forms
    class ThebloqImageForm(forms.ModelForm):
        class Meta:
            model = ThebloqImage
    if 'is_ckeditor' in request.GET:
        form = ThebloqImageForm(data=request.POST, files={'file': request.FILES['upload']})
        object = form.save()
        res =  "<script type='text/javascript'>window.parent.CKEDITOR.tools.callFunction(" + request.GET['CKEditorFuncNum'] + ", '" + object.get_list_item_info(request)['http_path']+ "');</script>"
        return HttpResponse(res)
    else:
        form = ThebloqImageForm(data=request.POST, files=request.FILES)
    object = form.save()
    return HttpResponse(json.dumps({'image': object.get_list_item_info(request)}))

class PictureCreateView(CreateView):

    model = ThebloqImage

    def form_valid(self, form):
        self.object = form.save()
        files = [serialize(self.object)]
        data = {
            'files': files
            #'image_url' : unicode(self.object.get_url()),
            #'pic_id'    : str(self.object.id),
            #'preview_url':str(get_thumbnail(self.object.file, '400x400', crop='center', quality=100).url),
            #'small_preview_url':str(get_thumbnail(self.object.file, '100x100', crop='center', quality=100).url)
        }
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return HttpResponse(content=data, status=400, content_type='application/json')


class PictureListView(ListView):
    model = ThebloqImage

    def get_queryset(self):
        if 'prod_id' in self.request.GET:
            imgs = ThebloqImage.objects.filter(object_id=self.request.GET['prod_id'], content_type=ContentType.objects.get_for_model(Product))
            return imgs
        elif 'gallery_id' in self.request.GET:
            imgs = ThebloqImage.objects.filter(object_id=self.request.GET['gallery_id'], content_type=ContentType.objects.get_for_model(GalleryItem))
            return imgs
        elif 'shop_id' in self.request.GET:
            #set = ShopSetting.objects.get(shop=Shop.objects.get(pk=self.request.GET['shop_id']))
            imgs = ThebloqImage.objects.filter(object_id=self.request.GET['shop_id'], content_type=ContentType.objects.get_for_model(ShopSetting))
            return imgs
        elif ('object_id' in self.request.GET) and ('content_type_id' in self.request.GET):
            imgs = ThebloqImage.objects.filter(object_id=self.request.GET['object_id'], content_type=self.request.GET['content_type_id'])
            return imgs
        else:
            return []

    def render_to_response(self, context, **response_kwargs):
        #files = [ serialize(p) for p in self.get_queryset() ]
        files = []
        for p in self.get_queryset  ():
            try:
                files.append(serialize(p))
            except Exception, e:
                logger.info(str(e))
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

# class PictureDeleteView(DeleteView):
#     model = ThebloqImage
#
#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         shop_settings = ShopSetting.objects.filter(logo_img=self.object)
#         for shop_setting in shop_settings:
#             shop_setting.logo_img = None
#             shop_setting.save()
#         self.object.delete()
#         response = JSONResponse(True, mimetype=response_mimetype(request))
#         response['Content-Disposition'] = 'inline; filename=files.json'
#         return response

class CreateVideo(CreateView):
    model = ThebloqVideo
    template_name = 'lugati_admin/videos/create_video.html'
    success_url = '/lugati_admin/'

    #form_class = CityForm

    def get_initial(self):
        res = {}
        cur_site = get_current_site(self.request)
        res['site'] = cur_site
        return res
    def form_invalid(self, form):
        if self.request.is_ajax():
            form_errors = {}
            for k in form.errors:
                form_errors[k] = form.errors[k][0]
            res_dt = {
                'error': True,
                'form_errors': form_errors
            }
            return HttpResponse(json.dumps(res_dt))
    def form_valid(self, form):
        self.object = form.save()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))

class UpdateVideo(UpdateView):
    model = ThebloqVideo
    template_name = 'lugati_admin/videos/update_video.html'
    success_url = '/lugati_admin/'

    def form_invalid(self, form):
        if self.request.is_ajax():
            res_dt = {
                'error': True
            }
            return HttpResponse(json.dumps(res_dt))
    def form_valid(self, form):
        self.object = form.save()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))

def get_videos_control_panel(request):
    return render(request, 'lugati_admin/videos/videos_control_panel.html')

def api_video(request, id=''):
    res_dt = []
    cur_site = get_current_site(request)
    videos = ThebloqVideo.objects.filter(site=cur_site)
    for video in videos:
        node = {
            'name': video.name,
            'video_code': video.video_code,
            'video_id': video.video_id,
            'vimeo_id': video.vimeo_id
        }
        images = lugati_procs.get_object_images(video)

        if images.count() > 0:
            node['thumbnail_url'] = images[0].get_thumbnail('368x276', crop=None, get_native_image=True).url
        else:
            if video.vimeo_id == '':
                try:
                    tb_image = lugati_procs.download_image('http://img.youtube.com/vi/' + str(video.video_id) + '/0.jpg')
                    tb_image.content_object = video
                    tb_image.save()
                    node['thumbnail_url'] = tb_image.get_thumbnail('368x276', crop=None, get_native_image=True).url
                except:
                    node['thumbnail_url'] = ''
            else:
                try:
                    r = requests.get('http://vimeo.com/api/v2/video/' + str(video.vimeo_id) + '.json')
                    # node['thumbnail_url'] = r.json()[0]['thumbnail_large']
                    tb_image = lugati_procs.download_image(r.json()[0]['thumbnail_large'])
                    tb_image.content_object = video
                    tb_image.save()
                    node['thumbnail_url'] = tb_image.get_thumbnail('368x276', crop=None, get_native_image=True).url
                except:
                    node['thumbnail_url'] = ''
        res_dt.append(node)
    return HttpResponse(json.dumps(res_dt))
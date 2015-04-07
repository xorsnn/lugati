from django.conf.urls import patterns, include, url

from .views import CreateGalleryItem, UpdateGalleryItem, DeleteGalleryItem

urlpatterns = patterns('',
    url(r'^create_gallery_item/$', CreateGalleryItem.as_view(), name='create_gallery_item'),
    url(r'^update_gallery_item/$', UpdateGalleryItem.as_view(), name='update_gallery_item'),
    url(r'^delete_gallery_item/$', DeleteGalleryItem.as_view(), name='delete_gallery_item'),

    url(r'^get_images/$', 'lugati.lugati_media.lugati_gallery.views.get_images', name='get_images'),
    url(r'^get_videos/$', 'lugati.lugati_media.lugati_gallery.views.get_videos', name='get_videos'),

    url(r'^get_galleries/$', 'lugati.lugati_media.lugati_gallery.views.get_galleries', name='get_galleries'),
    url(r'^get_gallery_images/(?P<gallery_id>\w+)/$', 'lugati.lugati_media.lugati_gallery.views.get_gallery_images', name='get_gallery_images'),
    url(r'^update_gallery_images/(?P<gallery_id>\w+)/$', 'lugati.lugati_media.lugati_gallery.views.update_gallery_images', name='update_gallery_images'),
    url(r'^get_update_gallery_template/(?P<gallery_id>\w+)/$', 'lugati.lugati_media.lugati_gallery.views.get_update_gallery_template', name='get_update_gallery_template'),
)

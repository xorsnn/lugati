from django.conf.urls import patterns, include, url
from .views import PictureCreateView, PictureListView#, PictureDeleteView
from .views import CreateVideo, UpdateVideo

urlpatterns = patterns('',
    #url(r'^remove_image/(?P<image_id>\w+)/$', 'lugati.lugati_media.views.remove_image', name='remove_image'),
    # url(r'^delete/(?P<pk>\d+)$', PictureDeleteView.as_view(), name='lugati_remove_image'),
    url(r'^delete/(?P<image_id>\d+)/$', 'lugati.lugati_media.views.remove_image', name='remove_image'),
    #url(r'^upload_image/$', 'lugati.lugati_media.views.upload_image', name='upload_image'),
    url(r'^upload_image/$', PictureCreateView.as_view(), name='upload_image'),
    url(r'^upload_image_new/$', 'lugati.lugati_media.views.upload_image_new', name='upload_image_new'),
    url(r'^get_images/$', PictureListView.as_view(), name='get_images'),


    url(r'^videos/update/(?P<pk>\d+)/$', UpdateVideo.as_view(), name='update_video'),
    url(r'^videos/create/$', CreateVideo.as_view(), name='create_video'),
    url(r'^get_videos_control_panel/$', 'lugati.lugati_media.views.get_videos_control_panel', name='get_videos_control_panel'),

    url(r'^mps_get_image/(?P<image_id>\d+)/$', 'lugati.lugati_media.views.mps_get_image', name='mps_get_image'),
    url(r'^mps_crop_image/(?P<content_object_id>\d+)/(?P<image_id>\d+)/$', 'lugati.lugati_media.views.mps_crop_image', name='mps_crop_image'),
    url(r'^mps_assign_image/(?P<content_object_id>\d+)/(?P<object_id>\d+)/(?P<image_id>\d+)/$', 'lugati.lugati_media.views.mps_assign_image', name='mps_assign_image'),
    url(r'^mps_assign_thumbnail/(?P<content_object_id>\d+)/(?P<object_id>\d+)/(?P<image_id>\d+)/$', 'lugati.lugati_media.views.mps_assign_thumbnail', name='mps_assign_thumbnail'),

    url(r'^get_aspect_ratio/(?P<content_object_id>\d+)/$', 'lugati.lugati_media.views.get_aspect_ratio', name='get_aspect_ratio'),

)

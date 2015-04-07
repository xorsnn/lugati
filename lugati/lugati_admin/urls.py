# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

# from .views import LugatiLogin

urlpatterns = patterns('',

    url(r'^$', 'lugati.lugati_admin.views.new_lugati_admin', name='lugati_admin'),

    url(r'^check_licensing/$', 'lugati.lugati_admin.views.check_licensing', name='check_licensing'),
    url(r'^accept_license/$', 'lugati.lugati_admin.views.accept_license', name='accept_license'),

    # url(r'^get_tooltip/(?P<object_id>\w+)/$', 'lugati.lugati_admin.views.get_tooltip', name='get_tooltip'),

    #super_new
    url(r'^lugati_editing_template/$', 'lugati.lugati_admin.views.lugati_editing_template', name='lugati_editing_template'),
    url(r'^get_objects_list_form/$', 'lugati.lugati_admin.views.get_objects_list_form', name='get_objects_list_form'),
    url(r'^get_objects_list_form/(?P<content_object_id>\w+)/$', 'lugati.lugati_admin.views.get_objects_list_form', name='get_objects_list_form'),
    url(r'^get_objects_list_form/(?P<content_object_id>\w+)/(?P<cat_id>\w+)/$', 'lugati.lugati_admin.views.get_objects_list_form', name='get_objects_list_form'),
    url(r'^get_edit_object_form/(?P<content_object_id>\w+)/(?P<object_id>\w+)/$', 'lugati.lugati_admin.views.get_edit_object_form', name='get_edit_object_form'),
    url(r'^get_create_object_form/(?P<content_object_id>\w+)/$', 'lugati.lugati_admin.views.get_create_object_form', name='get_create_object_form'),
    #~super_new

    #new lugati admin
    url(r'^get_editing_template/$', 'lugati.lugati_admin.views.get_editing_template', name='get_editing_template'),



    url(r'^new_admin/$', 'lugati.lugati_admin.views.new_lugati_admin', name='new_lugati_admin'),

    url(r'^main/$', 'lugati.lugati_admin.views.main', name='main'),
    url(r'^first_start/$', 'lugati.lugati_admin.views.first_start', name='first_start'),
    url(r'^user_settings/$', 'lugati.lugati_admin.views.user_settings', name='user_settings'),
    url(r'^company_settings/$', 'lugati.lugati_admin.views.company_settings', name='company_settings'),

    url(r'^get_tree_template/$', 'lugati.lugati_admin.views.get_tree_template', name='get_tree_template'),

    url(r'^lugati_products_admin/', include('lugati.products.urls_admin', namespace='lugati_products_admin')),

    url(r'^lugati_shop_admin/', include('lugati.lugati_shop.urls_admin', namespace='lugati_shop_admin')),
    url(r'^shops/$', 'lugati.lugati_admin.views.shops', name='shops'),#????????

    url(r'^lugati_points_of_sale_admin/', include('lugati.lugati_points_of_sale.urls_admin', namespace='lugati_points_of_sale_admin')),

    #~new lugati admin

    #modules
    url(r'^points_of_sale/', include('lugati.lugati_points_of_sale.urls', namespace='lugati_points_of_sale')),
    url(r'^lugati_shop/', include('lugati.lugati_shop.urls', namespace='lugati_shop')),
    url(r'^lugati_gallery/', include('lugati.lugati_media.lugati_gallery.urls', namespace='lugati_gallery')),
    url(r'^lugati_media/', include('lugati.lugati_media.urls', namespace='lugati_media')),
    url(r'^lugati_orders/', include('lugati.lugati_shop.lugati_orders.urls', namespace='lugati_orders')),
    #~modules

    #url(r'^phone_notification/$', ListPhoneNumbers.as_view(), name = 'list phone numbers'),
    #url(r'^phone_notification/create_phone_number/$', CreatePhoneNumber.as_view(), name = 'create phone number'),
    #url(r'^phone_notification/delete_phone_number/(?P<pk>\w+)/$', DeletePhoneNumber.as_view(), name = 'delete phone number'),

    url(r'^check_if_logged_in/', 'lugati.lugati_admin.views.check_if_logged_in', name='check_if_logged_in'),
    url(r'^device_login/', 'lugati.lugati_admin.views.device_login', name='device_login'),

    # login
    url(r'^lugati_login/', 'lugati.lugati_admin.views.lugati_login', name='lugati_login'),
    url(r'^lugati_register/', 'lugati.lugati_admin.views.lugati_register', name='lugati_register'),
    url(r'^password_restore/', 'lugati.lugati_admin.views.password_restore', name='password_restore'),
    url(r'^password_restore_request/', 'lugati.lugati_admin.views.password_restore_request', name='password_restore_request'),

    # url(r'^lugati_login/', LugatiLogin.as_view(), name='lugati_login'),
    # ~

    url(r'^lugati_logout/', 'lugati.lugati_admin.views.lugati_logout', name='lugati_logout'),
    url(r'^lugati_ajax_logout/', 'lugati.lugati_admin.views.lugati_ajax_logout', name='lugati_ajax_logout'),

    url(r'^products_ajax/', include('lugati.products.urls', namespace='lugati_products')),
)

from django.conf.urls import patterns, include, url
from .views import CreateOrder, UpdateOrder, DeleteOrder, DetailOrder

urlpatterns = patterns('',

    url(r'^pdf_receipt/(?P<object_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.pdf_receipt', name='pdf_receipt'),

    url(r'^change_order_state/(?P<order_id>\w+)/(?P<state_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.change_order_state', name='change_order_state'),

    url(r'^get_orders_list_channel_address/$', 'lugati.lugati_shop.lugati_orders.views.get_orders_list_channel_address', name='get_orders_list_channel_address'),
    url(r'^get_channel_address/$', 'lugati.lugati_shop.lugati_orders.views.get_channel_address', name='get_channel_address'),

    url(r'^order_details/(?P<pk>\w+)/$', DetailOrder.as_view(), name='detail_order'),


    url(r'^get_pdf_order/(?P<order_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.get_pdf_order', name='get_pdf_order'),
    url(r'^send_order_link_to_email/(?P<order_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.send_order_link_to_email', name='send_order_link_to_email'),
    #API Templates
    url(r'^lugati_get_order_details_template/$', 'lugati.lugati_shop.lugati_orders.views.lugati_get_order_details_template', name='lugati_get_order_details_template'),
    #url(r'^lugati_get_order_details_template_admin/$', 'lugati.lugati_shop.lugati_orders.views.lugati_get_order_details_template_admin', name='lugati_get_order_details_template_admin'),
    url(r'^lugati_get_orders_template/$', 'lugati.lugati_shop.lugati_orders.views.lugati_get_orders_template', name='lugati_get_orders_template'),

    #REST API
    #url(r'^get_orders/$', 'lugati.lugati_shop.lugati_orders.views.get_orders', name='get_orders'),

    url(r'^lugati_get_orders/$', 'lugati.lugati_shop.lugati_orders.views.lugati_get_orders', name='lugati_get_orders'),

    url(r'^lugati_get_order_details/(?P<order_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.lugati_get_order_details', name='lugati_get_order_details'),
    url(r'^lugati_update_order/(?P<order_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.lugati_update_order', name='lugati_update_order'),
    url(r'^lugati_update_order_state/(?P<order_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.lugati_update_order_state', name='lugati_update_order_state'),
    url(r'^lugati_check_order_state/(?P<order_id>\w+)/$', 'lugati.lugati_shop.lugati_orders.views.lugati_check_order_state', name='lugati_check_order_state'),
)
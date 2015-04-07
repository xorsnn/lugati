from django.conf.urls import patterns, include, url
from .views_admin import UpdateDeliveryOption, CreateDeliveryOption

urlpatterns = patterns('',
    url(r'^delivery_option/create/$', CreateDeliveryOption.as_view(), name='create_delivery_option'),
    url(r'^delivery_option/update/(?P<pk>\w+)/$', UpdateDeliveryOption.as_view(), name='update_delivery_option'),

    url(r'^get_delivery_options_tree/$', 'lugati.lugati_shop.lugati_delivery.views_admin.get_delivery_options_tree', name='get_delivery_options_tree'),
    url(r'^get_delivery_control_panel/$', 'lugati.lugati_shop.lugati_delivery.views_admin.get_delivery_control_panel', name='get_delivery_control_panel'),
    #poses MPS!!!
    #url(r'^point_of_sale/(?P<pos_id>\w+)/$', 'lugati.lugati_shop.views.pos_catalog', name='pos_catalog'),
    #~poses

)

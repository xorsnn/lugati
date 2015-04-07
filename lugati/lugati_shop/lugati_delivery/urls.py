from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^get_delivery_options/(?P<region_id>\w+)/$', 'lugati.lugati_shop.lugati_delivery.views.get_delivery_options', name='get_delivery_options'),
    url(r'^lugati_update_delivery_option/(?P<delivery_option_id>\w+)/$', 'lugati.lugati_shop.lugati_delivery.views.lugati_update_delivery_option', name='lugati_update_delivery_option'),
)

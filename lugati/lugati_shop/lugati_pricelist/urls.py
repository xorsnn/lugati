from django.conf.urls import patterns, include, url
from .views import ListPriceLists, CreatePricelist, UpdatePriceList#, CreatePricelistItem

urlpatterns = patterns('',
    url(r'^get_pricelists/$', 'lugati.lugati_shop.lugati_pricelist.views.manage_pricelists_ajax_new', name='get_pricelists'),

    url(r'^$', ListPriceLists.as_view(), name='list_price_lists'),

    url(r'^create/$', CreatePricelist.as_view(), name='create_pricelist'),
    url(r'^update/(?P<pk>\w+)/$', UpdatePriceList.as_view(), name='update_pricelist'),
    #url(r'^$', CreateCity.as_view(), name='create_city'),
    #url(r'^cities/update/(?P<pk>\w+)/$', UpdateCity.as_view(), name='update_city'),
)
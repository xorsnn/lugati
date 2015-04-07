
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^can_add_to_cart/(?P<prod_id>\w+)/$', 'lugati.lugati_shop.lugati_cart.views.can_add_to_cart', name='can_add_to_cart'),
)
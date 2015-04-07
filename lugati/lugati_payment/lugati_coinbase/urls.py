from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^get_coinbase_invoce/$', 'lugati.lugati_payment.lugati_coinbase.views.get_coinbase_invoce', name='get_coinbase_invoce'),
    url(r'^callback/$', 'lugati.lugati_payment.lugati_coinbase.views.coinbase_callback', name='coinbase_callback'),
    url(r'^callback/(?P<ticket>\w+)/$', 'lugati.lugati_payment.lugati_coinbase.views.coinbase_callback', name='coinbase_callback'),

    url(r'^check_if_order_paid/$', 'lugati.lugati_payment.lugati_coinbase.views.check_if_order_paid', name='check_if_order_paid'),

    # url(r'^callback_testing/$', 'lugati.lugati_payment.lugati_coinbase.views.coinbase_callback_testing', name='coinbase_callback_testing'),
)

from django.conf.urls import patterns, include, url


urlpatterns = patterns('',

    url(r'^lugati_coinbase/', include('lugati.lugati_payment.lugati_coinbase.urls', namespace='lugati_coinbase')),
    url(r'^lugati_robokassa/', include('lugati.lugati_payment.lugati_robokassa.urls', namespace='lugati_robokassa')),
    url(r'^lugati_stripe/', include('lugati.lugati_payment.lugati_stripe.urls', namespace='lugati_stripe')),

    # procs
    url(r'^get_btc_invoice/', 'lugati.lugati_payment.views.get_btc_invoice', name='get_btc_invoice'),

    url(r'^get_qr_code/', 'lugati.lugati_payment.views.get_qr_code', name='get_qr_code'),

    url(r'^get_btc_balance/', 'lugati.lugati_payment.views.get_btc_balance', name='get_btc_balance'),

    url(r'^send_btc/', 'lugati.lugati_payment.views.send_btc', name='send_btc'),
    url(r'^get_btc_balance_channel_address/', 'lugati.lugati_payment.views.get_btc_balance_channel_address', name='get_btc_balance_channel_address'),
)

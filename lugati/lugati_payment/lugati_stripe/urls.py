from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^stripe_connect/$', 'lugati.lugati_payment.lugati_stripe.views.stripe_connect', name='stripe_connect'),
    url(r'^get_public_key/$', 'lugati.lugati_payment.lugati_stripe.views.get_public_key', name='get_public_key'),
    url(r'^stripe_callback/$', 'lugati.lugati_payment.lugati_stripe.views.stripe_callback', name='stripe_callback'),

)

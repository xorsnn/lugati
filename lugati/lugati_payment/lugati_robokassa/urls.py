from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    #url(r'^', include('robokassa.urls')),
    url(r'^result/$', 'lugati.lugati_payment.lugati_robokassa.views.result', name='lugati_robokassa_result'),
    url(r'^success/$', 'lugati.lugati_payment.lugati_robokassa.views.success', name='lugati_robokassa_success'),
    url(r'^fail/$', 'lugati.lugati_payment.lugati_robokassa.views.fail', name='lugati_robokassa_fail'),
    url(r'^get_payment_template/(?P<order_id>\w+)/$', 'lugati.lugati_payment.lugati_robokassa.views.get_payment_template', name='lugati_robokassa_get_payment_template'),
    url(r'^get_payment_template/$', 'lugati.lugati_payment.lugati_robokassa.views.get_payment_template', name='lugati_robokassa_get_payment_template'),
)

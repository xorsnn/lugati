from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^api/', include('lugati.api_urls', namespace='api')),
    url(r'^products/', include('lugati.products.urls', namespace='products')),
    url(r'^catalog/', include('lugati.lugati_shop.urls', namespace='shop')),
    url(r'^payment/', include('lugati.lugati_payment.urls', namespace='lugati_payment')),

    url(r'^lugati_feedback/', include('lugati.lugati_feedback.urls')),

    url(r'^lugati_media/', include('lugati.lugati_media.urls', namespace='lugati_media')),
    url(r'^lugati_admin/', include('lugati.lugati_admin.urls')),

#registration
    url(r'^lugati_registration/', include('lugati.lugati_registration.urls')),
#~registration
    url(r'^', include('lugati.lugati_static.urls', namespace='lugati_static')),
)
